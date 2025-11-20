from google import genai
from typing import List, Dict
import sys
sys.path.append('..')
from tools.pubmed_tool import PubMedTool
from utils.retry_utils import async_retry_with_backoff
from config import Config

class LiteratureSearchAgent:
    """Agent that searches medical literature for matching conditions"""
    
    def __init__(self, client: genai.Client, pubmed_tool: PubMedTool):
        self.client = client
        self.pubmed_tool = pubmed_tool
    
    @async_retry_with_backoff(max_retries=Config.MAX_RETRIES)
    async def search_conditions(self, symptoms: Dict) -> List[Dict]:
        """
        Search medical literature for conditions matching symptoms
        
        Args:
            symptoms: Structured symptom data from SymptomAggregator
            
        Returns:
            List of potential conditions with evidence
        """
        
        # Step 1: Generate search queries using Gemini
        query_generation_prompt = f"""Based on these symptoms, generate 3-5 targeted PubMed search queries to find rare diseases that match:

Symptoms: {symptoms.get('primary_symptoms', [])}
Timeline: {symptoms.get('timeline', '')}
Severity: {symptoms.get('severity', '')}

Generate queries that:
1. Combine key symptoms
2. Include relevant medical terms
3. Focus on rare/uncommon conditions
4. Use specific diagnostic terminology

Return as JSON array: ["query1", "query2", "query3"]"""

        try:
            # Generate search queries
            response = await self.client.aio.models.generate_content(
                model=Config.MODEL_NAME,
                contents=query_generation_prompt
            )
            
            # Parse queries
            queries = self._extract_queries(response.text)
            print(f"  DEBUG: Generated {len(queries)} search queries")
            for i, q in enumerate(queries[:3], 1):
                print(f"    {i}. {q[:80]}...")
            
            # Step 2: Search PubMed with each query
            all_articles = []
            for query in queries[:3]:  # Limit to 3 queries
                articles = self.pubmed_tool.search(query, max_results=10)
                print(f"  DEBUG: PubMed returned {len(articles)} articles for query: {query[:50]}...")
                all_articles.extend(articles)
            
            print(f"  DEBUG: Total articles collected: {len(all_articles)}")
            
            # Step 3: Analyze articles to extract conditions
            conditions = await self._analyze_articles(all_articles, symptoms)
            print(f"  DEBUG: Extracted {len(conditions)} conditions from articles")
            
            return conditions
            
        except Exception as e:
            print(f"Error in literature search: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _extract_queries(self, response: str) -> List[str]:
        """Extract search queries from LLM response"""
        import json
        import re
        
        try:
            # Try to parse JSON array
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback: split by newlines
        queries = [line.strip() for line in response.split('\n') if line.strip()]
        return queries[:5]
    
    @async_retry_with_backoff(max_retries=Config.MAX_RETRIES)
    async def _analyze_articles(self, articles: List[Dict], symptoms: Dict) -> List[Dict]:
        """Analyze articles to identify potential conditions"""
        
        analysis_prompt = f"""Analyze these medical research articles and identify rare diseases that match the patient's symptoms.

Patient symptoms: {symptoms.get('primary_symptoms', [])}

Articles:
{self._format_articles_for_analysis(articles[:10])}

For each potential rare disease, provide:
1. Condition name
2. Matching symptoms (how patient symptoms align)
3. Confidence score (0.0-1.0)
4. Key diagnostic criteria
5. Supporting evidence from articles

Return as JSON array of conditions."""

        try:
            response = await self.client.aio.models.generate_content(
                model=Config.MODEL_NAME,
                contents=analysis_prompt
            )
            
            # Parse conditions
            conditions = self._parse_conditions(response.text)
            
            return conditions
            
        except Exception as e:
            print(f"Error analyzing articles: {e}")
            return []
    
    def _format_articles_for_analysis(self, articles: List[Dict]) -> str:
        """Format articles for LLM analysis"""
        formatted = []
        for i, article in enumerate(articles[:5], 1):
            formatted.append(f"{i}. {article['title']}\n   Abstract: {article['abstract'][:200]}...")
        return "\n\n".join(formatted)
    
    def _parse_conditions(self, response: str) -> List[Dict]:
        """Parse conditions from LLM response"""
        import json
        import re
        
        try:
            # Try to parse JSON array
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                conditions = json.loads(json_match.group())
                
                # Normalize condition format
                normalized = []
                for cond in conditions:
                    # Handle different field names
                    condition_name = (
                        cond.get('name') or 
                        cond.get('condition') or 
                        cond.get('condition_name') or
                        cond.get('diagnosis') or
                        'Unknown Condition'
                    )
                    
                    normalized.append({
                        'name': condition_name,
                        'confidence': cond.get('confidence', cond.get('confidence_score', 0.5)),
                        'matching_symptoms': cond.get('matching_symptoms', cond.get('symptoms', [])),
                        'diagnostic_tests': cond.get('diagnostic_tests', cond.get('tests', [])),
                        'evidence': cond.get('evidence', cond.get('supporting_evidence', ''))
                    })
                
                return normalized
        except Exception as e:
            print(f"Error parsing conditions JSON: {e}")
        
        # Fallback: extract condition names from text
        conditions = []
        lines = response.split('\n')
        for line in lines:
            # Look for patterns like "1. Condition Name" or "- Condition Name"
            match = re.match(r'[\d\-\•]\s*\.?\s*([A-Z][^:\n]{5,80})', line.strip())
            if match:
                condition_name = match.group(1).strip()
                if any(keyword in condition_name.lower() for keyword in ['syndrome', 'disease', 'disorder', 'condition']):
                    conditions.append({
                        'name': condition_name,
                        'confidence': 0.6,
                        'matching_symptoms': [],
                        'diagnostic_tests': [],
                        'evidence': ''
                    })
        
        return conditions[:5]  # Return top 5
