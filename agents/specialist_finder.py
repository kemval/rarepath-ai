import requests
from typing import List, Dict
from google import genai
from utils.retry_utils import async_retry_with_backoff
from config import Config

class GoogleSearchTool:
    """Tool for web search using Gemini's built-in Google Search"""
    
    def __init__(self, client: genai.Client):
        self.client = client
    
    @async_retry_with_backoff(max_retries=Config.MAX_RETRIES)
    async def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search the web using Gemini with Google Search grounding
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of search results
        """
        try:
            # Use Gemini with Google Search grounding
            response = await self.client.aio.models.generate_content(
                model=Config.MODEL_NAME,
                contents=f"Search for: {query}. Provide the top {max_results} most relevant results with titles, URLs, and brief descriptions.",
                config={
                    'tools': [{'google_search': {}}]  # Enable Google Search
                }
            )
            
            # Parse results
            results = self._parse_search_results(response.text)
            return results
            
        except Exception as e:
            print(f"Error in Google search: {e}")
            return []
    
    def _parse_search_results(self, response_text: str) -> List[Dict]:
        """Parse search results from response"""
        # For now, return the raw text
        # In production, parse structured results
        return [{'content': response_text}]

# ----------------------------------------------------------------------------
# FILE 12: agents/specialist_finder.py
# ----------------------------------------------------------------------------

from google import genai
from typing import List, Dict
import sys
sys.path.append('..')

class SpecialistFinderAgent:
    """Agent that finds medical specialists for suspected conditions"""
    
    def __init__(self, client: genai.Client):
        self.client = client
    
    async def find_specialists(
        self, 
        conditions: List[Dict], 
        location: str = "United States"
    ) -> List[Dict]:
        """
        Find specialists who treat the suspected conditions
        
        Args:
            conditions: List of potential conditions from literature search
            location: Patient's location for proximity search
            
        Returns:
            List of specialists with contact information
        """
        
        if not conditions:
            return []
        
        # Get top 3 most likely conditions
        top_conditions = sorted(
            conditions, 
            key=lambda x: x.get('confidence', 0), 
            reverse=True
        )[:3]
        
        all_specialists = []
        
        for condition in top_conditions:
            condition_name = condition.get('name', '')
            
            # Generate search strategy
            specialist_prompt = f"""You need to help find medical specialists for a patient with suspected {condition_name}.

Task: Identify the types of medical specialists who typically diagnose and treat {condition_name}.

Provide:
1. Primary specialist type (e.g., "Geneticist", "Rheumatologist", "Cardiologist")
2. Secondary specialist types that may be involved
3. What to look for in a specialist (experience, certifications, research focus)
4. Search terms to find these specialists

Return as JSON:
{{
    "primary_specialty": "...",
    "secondary_specialties": ["...", "..."],
    "key_qualifications": ["...", "..."],
    "search_terms": ["...", "..."]
}}"""

            try:
                response = await self.client.aio.models.generate_content(
                    model=Config.MODEL_NAME,
                    contents=specialist_prompt
                )
                
                specialty_info = self._parse_specialty_info(response.text)
                
                # Now search for actual specialists
                specialists = await self._search_specialists(
                    specialty_info, 
                    condition_name,
                    location
                )
                
                all_specialists.extend(specialists)
                
            except Exception as e:
                print(f"Error finding specialists for {condition_name}: {e}")
                continue
        
        # Deduplicate and rank specialists
        return self._deduplicate_specialists(all_specialists)
    
    def _parse_specialty_info(self, response: str) -> Dict:
        """Parse specialty information from LLM response"""
        import json
        import re
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "primary_specialty": "Specialist",
            "search_terms": []
        }
    
    @async_retry_with_backoff(max_retries=Config.MAX_RETRIES)
    async def _search_specialists(
        self, 
        specialty_info: Dict, 
        condition: str,
        location: str
    ) -> List[Dict]:
        """Search for specialists using web search"""
        
        primary_specialty = specialty_info.get('primary_specialty', '')
        
        # Construct search query
        search_query = f"{primary_specialty} specialist {condition} {location}"
        
        # Use Gemini with Google Search
        search_prompt = f"""Find medical specialists and treatment centers for {condition} in {location}.

Focus on finding:
- Major medical centers with {primary_specialty} departments
- Individual specialists with {condition} expertise
- Academic medical centers doing research on {condition}

Provide top 5 results with:
- Name of doctor/center
- Location
- Specialty focus
- Contact information (if available)
- Why they're relevant for {condition}"""

        try:
            response = await self.client.aio.models.generate_content(
                model=Config.MODEL_NAME,
                contents=search_prompt,
                config={
                    'tools': [{'google_search': {}}]
                }
            )
            
            # Parse specialist information
            specialists = self._parse_specialists(response.text, condition)
            
            return specialists
            
        except Exception as e:
            print(f"Error searching specialists: {e}")
            return []
    
    def _parse_specialists(self, response: str, condition: str) -> List[Dict]:
        """Parse specialist information from search results"""
        
        # For now, create structured output from response
        # In production, would parse more carefully
        return [{
            'condition': condition,
            'search_results': response,
            'type': 'specialist_recommendations'
        }]
    
    def _deduplicate_specialists(self, specialists: List[Dict]) -> List[Dict]:
        """Remove duplicate specialists"""
        # Simple deduplication by condition
        seen = set()
        unique = []
        
        for spec in specialists:
            condition = spec.get('condition', '')
            if condition not in seen:
                seen.add(condition)
                unique.append(spec)
        
        return unique