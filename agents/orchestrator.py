from google import genai
from typing import Dict, List
import asyncio
import time
from agents.symptom_aggregator import SymptomAggregatorAgent
from agents.literature_search_agent import LiteratureSearchAgent
from agents.specialist_finder import SpecialistFinderAgent
from agents.history_compiler import HistoryCompilerAgent
from agents.community_connector import CommunityConnectorAgent
from tools.pubmed_tool import PubMedTool
from tools.clinical_trials_tool import ClinicalTrialsTool
from utils.memory import SessionManager, MemoryBank
from utils.logger import RarePathLogger
from utils.retry_utils import RateLimiter
from config import Config

class RarePathOrchestrator:
    """
    Master orchestrator coordinating all agents in the diagnostic journey
    NOW WITH: All 7 agents, memory, logging, and full workflow
    """
    
    def __init__(self, api_key: str):
        # Initialize Gemini client
        self.client = genai.Client(api_key=api_key)
        
        # Initialize tools
        self.pubmed_tool = PubMedTool()
        self.trials_tool = ClinicalTrialsTool()
        
        # Initialize ALL agents
        self.symptom_agent = SymptomAggregatorAgent(self.client)
        self.literature_agent = LiteratureSearchAgent(self.client, self.pubmed_tool)
        self.specialist_agent = SpecialistFinderAgent(self.client)
        self.history_agent = HistoryCompilerAgent(self.client)
        self.community_agent = CommunityConnectorAgent(self.client)
        
        # Initialize memory and logging
        self.session_manager = SessionManager()
        self.memory_bank = MemoryBank()
        self.logger = RarePathLogger()
        
        # Initialize rate limiter to prevent quota exhaustion
        self.rate_limiter = RateLimiter(calls_per_minute=Config.RATE_LIMIT_CALLS_PER_MINUTE)
    
    async def run_diagnostic_journey(
        self, 
        patient_input: str, 
        session_id: str = "default",
        patient_location: str = "United States"
    ) -> Dict:
        """
        Complete diagnostic journey with all agents
        """
        
        start_time = time.time()
        
        print("🏥 RarePath AI - Starting comprehensive diagnostic journey...")
        print("=" * 60)
        
        # Create session
        self.session_manager.create_session(session_id)
        self.logger.log_agent_call("Orchestrator", "start_journey")
        
        # Track warnings for failed API calls
        warnings = {
            'conditions_failed': False,
            'trials_failed': False,
            'specialists_failed': False,
            'communities_failed': False
        }
        
        try:
            # STEP 1: Symptom Collection (Sequential)
            print("\n📋 Step 1: Collecting symptom information...")
            self.logger.log_agent_call("SymptomAggregator", "collect")
            
            await self.rate_limiter.acquire()  # Rate limit
            symptoms = await self.symptom_agent.collect_symptoms(patient_input, session_id)
            self.memory_bank.store_session(session_id, {'symptoms': symptoms})
            
            print(f"✓ Identified {len(symptoms.get('primary_symptoms', []))} primary symptoms")
            
            # STEP 2: Parallel Search Phase
            print("\n🔍 Step 2: Running parallel searches...")
            print("  → Searching medical literature...")
            print("  → Finding specialists...")
            print("  → Matching clinical trials...")
            print("  → Connecting communities...")
            
            self.logger.log_agent_call("ParallelSearch", "start")
            
            # Rate limit before parallel search
            await self.rate_limiter.acquire()
            
            # Run all search agents in parallel
            results = await asyncio.gather(
                self.literature_agent.search_conditions(symptoms),
                self._search_clinical_trials(symptoms),
                return_exceptions=True
            )
            
            literature_results = results[0] if not isinstance(results[0], Exception) else []
            trial_results = results[1] if not isinstance(results[1], Exception) else []
            
            if isinstance(results[0], Exception):
                print(f"⚠️  Literature search encountered an error: {type(results[0]).__name__}: {str(results[0][:200])}")
                import traceback
                traceback.print_exception(type(results[0]), results[0], results[0].__traceback__)
                warnings['conditions_failed'] = True
            if isinstance(results[1], Exception):
                print(f"⚠️  Clinical trials search encountered an error: {type(results[1]).__name__}: {str(results[1])[:200]}")
                import traceback
                traceback.print_exception(type(results[1]), results[1], results[1].__traceback__)
                warnings['trials_failed'] = True
            
            # Store in memory
            self.memory_bank.store_session(session_id, {
                'conditions': literature_results,
                'trials': trial_results
            })
            
            print(f"✓ Found {len(literature_results)} potential conditions")
            print(f"✓ Found {len(trial_results)} relevant clinical trials")
            
            # STEP 3: Find specialists (depends on conditions)
            print("\n👨‍⚕️ Step 3: Finding specialists...")
            self.logger.log_agent_call("SpecialistFinder", "find")
            
            await self.rate_limiter.acquire()  # Rate limit
            try:
                specialists = await self.specialist_agent.find_specialists(
                    literature_results,
                    patient_location
                )
                print(f"✓ Found {len(specialists)} specialist recommendations")
            except Exception as e:
                print(f"⚠️  Specialist search failed: {str(e)[:100]}")
                specialists = []
                warnings['specialists_failed'] = True
            
            # STEP 4: Find communities
            print("\n🤝 Step 4: Connecting with patient communities...")
            self.logger.log_agent_call("CommunityConnector", "find")
            
            await self.rate_limiter.acquire()  # Rate limit
            try:
                communities = await self.community_agent.find_communities(literature_results)
                print(f"✓ Found {len(communities)} community resources")
            except Exception as e:
                print(f"⚠️  Community search failed: {str(e)[:100]}")
                communities = []
                warnings['communities_failed'] = True
            
            # STEP 5: Compile comprehensive report
            print("\n📊 Step 5: Compiling comprehensive report...")
            self.logger.log_agent_call("HistoryCompiler", "compile")
            
            await self.rate_limiter.acquire()  # Rate limit
            report = await self.history_agent.compile_report(
                symptoms,
                literature_results,
                specialists,
                trial_results
            )
            
            # Add community resources to report
            report['community_resources'] = communities
            
            # Add warnings to report
            report['_warnings'] = warnings
            
            # Calculate metrics
            end_time = time.time()
            total_time = end_time - start_time
            
            self.logger.log_api_call("Orchestrator", "complete_journey", total_time)
            
            report['execution_metrics'] = {
                'total_time_seconds': total_time,
                'agents_used': 7,
                'api_calls': self.logger.get_metrics()
            }
            
            print("\n✓ Diagnostic journey complete!")
            print(f"  Total time: {total_time:.2f} seconds")
            print("=" * 60)
            
            # Print metrics summary
            self.logger.print_summary()
            
            return report
            
        except Exception as e:
            self.logger.log_error(e, "diagnostic_journey")
            print(f"\n❌ Error during diagnostic journey: {str(e)}")
            print("\n💡 Troubleshooting tips:")
            print("  • Check your internet connection")
            print("  • Verify your Gemini API key is valid and has quota remaining")
            print("  • Visit https://ai.google.dev/gemini-api/docs/rate-limits for rate limit info")
            print("  • Consider waiting a few minutes if you hit rate limits")
            raise
    
    async def _search_clinical_trials(self, symptoms: Dict) -> List[Dict]:
        """Search for clinical trials"""
        primary_symptoms = symptoms.get('primary_symptoms', [])
        if not primary_symptoms:
            return []
        
        trials = self.trials_tool.search(primary_symptoms[0], max_results=5)
        return trials
