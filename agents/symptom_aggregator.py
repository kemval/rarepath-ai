from google import genai
from typing import Dict, List
from utils.retry_utils import async_retry_with_backoff
from config import Config

class SymptomAggregatorAgent:
    """Agent responsible for collecting and organizing patient symptoms"""
    
    def __init__(self, client: genai.Client):
        self.client = client
        self.conversation_history = []
    
    @async_retry_with_backoff(max_retries=Config.MAX_RETRIES)
    async def collect_symptoms(self, initial_input: str, session_id: str) -> Dict:
        """
        Conduct structured interview to collect comprehensive symptom information
        
        Args:
            initial_input: Patient's initial description
            session_id: Session identifier for memory
            
        Returns:
            Structured symptom profile
        """
        
        # Initial symptom extraction prompt
        prompt = f"""You are a compassionate medical assistant helping a patient describe their symptoms.

Patient's initial description: "{initial_input}"

Your task:
1. Extract all symptoms mentioned
2. Ask clarifying questions about:
   - Timeline (when did symptoms start, how have they progressed)
   - Severity (mild, moderate, severe)
   - Frequency (constant, intermittent, triggered by specific activities)
   - Associated symptoms they might not have mentioned
   - Family history of similar conditions
   - Previous diagnoses or tests

Create a structured JSON output with:
{{
    "primary_symptoms": ["symptom1", "symptom2"],
    "timeline": "description of symptom progression",
    "severity": "overall severity assessment",
    "frequency": "frequency patterns",
    "family_history": "relevant family history",
    "previous_diagnoses": ["diagnosis1", "diagnosis2"],
    "questions_to_ask": ["question1", "question2"]
}}

Be empathetic and thorough."""

        try:
            response = await self.client.aio.models.generate_content(
                model=Config.MODEL_NAME,
                contents=prompt
            )
            
            # Store in conversation history
            self.conversation_history.append({
                'role': 'user',
                'content': initial_input
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': response.text
            })
            
            # Parse response (in real implementation, ensure JSON parsing)
            symptom_data = self._parse_symptom_response(response.text)
            
            return symptom_data
            
        except Exception as e:
            print(f"Error in symptom collection: {e}")
            return {
                "primary_symptoms": [],
                "timeline": "",
                "severity": "",
                "questions_to_ask": []
            }
    
    def _parse_symptom_response(self, response: str) -> Dict:
        """Parse LLM response into structured symptom data"""
        import json
        import re
        
        # Try to extract JSON from response
        try:
            # Look for JSON block
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback to basic structure
        return {
            "primary_symptoms": [],
            "timeline": "",
            "severity": "unknown",
            "questions_to_ask": [],
            "raw_response": response
        }
