from google import genai
from typing import List, Dict
from utils.retry_utils import async_retry_with_backoff
from config import Config

class GoogleSearchTool:
    """Tool for performing web searches using Gemini with Google Search grounding"""
    
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
