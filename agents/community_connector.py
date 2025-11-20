from google import genai
from typing import List, Dict
from utils.retry_utils import async_retry_with_backoff
from config import Config

class CommunityConnectorAgent:
    """Agent that finds patient communities and support resources"""
    
    def __init__(self, client: genai.Client):
        self.client = client
    
    async def find_communities(self, conditions: List[Dict]) -> List[Dict]:
        """
        Find patient advocacy groups and support communities
        
        Args:
            conditions: List of potential conditions
            
        Returns:
            List of community resources
        """
        
        if not conditions:
            return []
        
        communities = []
        
        # Get top 3 conditions
        top_conditions = sorted(
            conditions,
            key=lambda x: x.get('confidence', 0),
            reverse=True
        )[:3]
        
        for condition in top_conditions:
            condition_name = condition.get('name', '')
            
            # Search for communities
            community_prompt = f"""Find patient support communities and resources for people with {condition_name}.

Look for:
1. Official patient advocacy organizations (e.g., foundations, associations)
2. Online support groups (Reddit, Facebook groups)
3. Educational resources and websites
4. Patient conferences or events
5. Peer support networks

Provide:
- Organization/community name
- Type (advocacy group, online forum, etc.)
- URL (if available)
- Brief description
- Why it's helpful

Return top 5 resources."""

            try:
                response = await self.client.aio.models.generate_content(
                    model=Config.MODEL_NAME,
                    contents=community_prompt,
                    config={
                        'tools': [{'google_search': {}}]
                    }
                )
                
                community_data = {
                    'condition': condition_name,
                    'resources': response.text
                }
                
                communities.append(community_data)
                
            except Exception as e:
                print(f"Error finding communities for {condition_name}: {e}")
                continue
        
        return communities
