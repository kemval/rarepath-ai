from google import genai
from typing import Dict, List
import json
from utils.retry_utils import async_retry_with_backoff
from config import Config

class HistoryCompilerAgent:
    """Agent that compiles comprehensive medical reports"""
    
    def __init__(self, client: genai.Client):
        self.client = client
    
    async def compile_report(
        self,
        symptoms: Dict,
        conditions: List[Dict],
        specialists: List[Dict],
        trials: List[Dict]
    ) -> Dict:
        """
        Compile all findings into a comprehensive report
        
        Args:
            symptoms: Patient symptom data
            conditions: Potential diagnoses from literature
            specialists: Specialist recommendations
            trials: Clinical trial matches
            
        Returns:
            Comprehensive diagnostic report
        """
        
        # Generate patient summary
        patient_summary = await self._generate_patient_summary(symptoms)
        
        # Generate condition analysis
        condition_analysis = await self._analyze_conditions(conditions, symptoms)
        
        # Generate specialist recommendations
        specialist_recommendations = self._format_specialists(specialists)
        
        # Generate clinical trial summary
        trial_summary = self._format_trials(trials)
        
        # Generate next steps
        next_steps = await self._generate_next_steps(condition_analysis, symptoms)
        
        # Compile final report
        report = {
            'executive_summary': patient_summary,
            'symptom_profile': symptoms,
            'potential_diagnoses': condition_analysis,
            'specialist_recommendations': specialist_recommendations,
            'clinical_trials': trial_summary,
            'next_steps': next_steps,
            'timeline_visualization': self._create_timeline(symptoms),
            'questions_for_doctor': await self._generate_doctor_questions(condition_analysis),
            'disclaimer': self._get_disclaimer()
        }
        
        return report
    
    @async_retry_with_backoff(max_retries=Config.MAX_RETRIES)
    async def _generate_patient_summary(self, symptoms: Dict) -> str:
        """Generate executive summary of patient case"""
        
        prompt = f"""Create a concise executive summary (2-3 sentences) of this patient's case:

Primary Symptoms: {symptoms.get('primary_symptoms', [])}
Timeline: {symptoms.get('timeline', '')}
Severity: {symptoms.get('severity', '')}
Family History: {symptoms.get('family_history', '')}

Write in clear, compassionate language suitable for both the patient and their doctors."""

        try:
            response = await self.client.aio.models.generate_content(
                model=Config.MODEL_NAME,
                contents=prompt
            )
            return response.text.strip()
        except:
            return "Patient presents with multiple chronic symptoms requiring specialist evaluation."
    
    @async_retry_with_backoff(max_retries=Config.MAX_RETRIES)
    async def _analyze_conditions(self, conditions: List[Dict], symptoms: Dict) -> List[Dict]:
        """Analyze and rank potential conditions"""
        
        if not conditions:
            return []
        
        analysis_prompt = f"""Analyze these potential rare disease diagnoses in the context of the patient's symptoms.

Patient Symptoms: {symptoms.get('primary_symptoms', [])}

Potential Conditions:
{json.dumps(conditions[:5], indent=2)}

For each condition, provide:
1. Why this diagnosis fits the patient's presentation
2. Key diagnostic tests needed to confirm/rule out
3. Confidence level (High/Medium/Low)
4. What additional symptoms would increase confidence

Return as JSON array of analyzed conditions."""

        try:
            response = await self.client.aio.models.generate_content(
                model=Config.MODEL_NAME,
                contents=analysis_prompt
            )
            
            # Parse and return analyzed conditions
            return self._parse_condition_analysis(response.text, conditions)
            
        except Exception as e:
            print(f"Error analyzing conditions: {e}")
            return conditions  # Return original if analysis fails
    
    def _parse_condition_analysis(self, response: str, original_conditions: List[Dict]) -> List[Dict]:
        """Parse condition analysis from LLM"""
        import re
        
        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return original_conditions
    
    def _format_specialists(self, specialists: List[Dict]) -> List[Dict]:
        """Format specialist recommendations"""
        formatted = []
        
        for spec in specialists:
            formatted.append({
                'condition': spec.get('condition', ''),
                'recommendations': spec.get('search_results', ''),
                'priority': 'High' if 'academic' in spec.get('search_results', '').lower() else 'Medium'
            })
        
        return formatted
    
    def _format_trials(self, trials: List[Dict]) -> List[Dict]:
        """Format clinical trial information"""
        formatted = []
        
        for trial in trials[:5]:  # Top 5 trials
            formatted.append({
                'title': trial.get('title', ''),
                'nct_id': trial.get('nct_id', ''),
                'status': trial.get('status', ''),
                'url': trial.get('url', ''),
                'locations': trial.get('locations', [])[:3]  # Top 3 locations
            })
        
        return formatted
    
    @async_retry_with_backoff(max_retries=Config.MAX_RETRIES)
    async def _generate_next_steps(self, conditions: List[Dict], symptoms: Dict) -> List[str]:
        """Generate actionable next steps for patient"""
        
        prompt = f"""Based on these potential diagnoses and symptoms, generate 5-7 actionable next steps for the patient.

Potential Diagnoses: {[c.get('name', '') for c in conditions[:3]]}
Symptoms: {symptoms.get('primary_symptoms', [])}

Steps should be:
- Specific and actionable
- Prioritized by urgency
- Practical for a patient to accomplish
- Include both medical and self-care actions

Return as JSON array of strings."""

        try:
            response = await self.client.aio.models.generate_content(
                model=Config.MODEL_NAME,
                contents=prompt
            )
            
            return self._parse_next_steps(response.text)
            
        except:
            return [
                "Schedule appointment with primary care physician to discuss findings",
                "Request referrals to recommended specialists",
                "Keep detailed symptom diary including triggers and patterns",
                "Gather all previous medical records and test results",
                "Research patient advocacy groups for support"
            ]
    
    def _parse_next_steps(self, response: str) -> List[str]:
        """Parse next steps from LLM response"""
        import re
        
        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback: parse bullet points
        steps = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                steps.append(line.lstrip('-•0123456789. '))
        
        return steps if steps else ["Consult with your healthcare provider"]
    
    def _create_timeline(self, symptoms: Dict) -> Dict:
        """Create a visual timeline of symptom progression"""
        return {
            'type': 'timeline',
            'data': {
                'timeline_description': symptoms.get('timeline', ''),
                'key_milestones': [
                    'Symptom onset',
                    'Symptom progression',
                    'Current status'
                ]
            }
        }
    
    @async_retry_with_backoff(max_retries=Config.MAX_RETRIES)
    async def _generate_doctor_questions(self, conditions: List[Dict]) -> List[str]:
        """Generate questions for patient to ask their doctor"""
        
        condition_names = [c.get('name', '') for c in conditions[:3]]
        
        prompt = f"""Generate 5 important questions a patient should ask their doctor about these potential diagnoses:
{', '.join(condition_names)}

Questions should:
- Help confirm or rule out diagnoses
- Address treatment options
- Clarify next diagnostic steps
- Be clear and direct

Return as JSON array of strings."""

        try:
            response = await self.client.aio.models.generate_content(
                model=Config.MODEL_NAME,
                contents=prompt
            )
            
            return self._parse_next_steps(response.text)  # Same parsing logic
            
        except:
            return [
                "What tests can help confirm or rule out these conditions?",
                "Should I see a specialist, and if so, what type?",
                "Are there any treatments available for these conditions?",
                "What symptoms should I monitor most closely?",
                "Are there any lifestyle changes that could help?"
            ]
    
    def _get_disclaimer(self) -> str:
        """Get medical disclaimer"""
        return """IMPORTANT DISCLAIMER: This report is generated by an AI system for informational purposes only. 
It is NOT a medical diagnosis and should NOT replace professional medical advice. 
Always consult with qualified healthcare providers before making any medical decisions."""
