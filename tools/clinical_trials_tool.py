import requests
from typing import List, Dict

class ClinicalTrialsTool:
    """Tool for searching ClinicalTrials.gov"""
    
    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"
    
    def search(self, condition: str, max_results: int = 10) -> List[Dict]:
        """
        Search for clinical trials matching a condition
        
        Args:
            condition: Medical condition (e.g., "Ehlers-Danlos Syndrome")
            max_results: Maximum number of trials to return
            
        Returns:
            List of trial dictionaries
        """
        try:
            params = {
                'query.cond': condition,
                'filter.overallStatus': 'RECRUITING',  # Only active trials
                'pageSize': max_results,
                'format': 'json'
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            trials = []
            
            for study in data.get('studies', []):
                protocol = study.get('protocolSection', {})
                identification = protocol.get('identificationModule', {})
                description = protocol.get('descriptionModule', {})
                eligibility = protocol.get('eligibilityModule', {})
                contacts = protocol.get('contactsLocationsModule', {})
                
                trials.append({
                    'nct_id': identification.get('nctId', ''),
                    'title': identification.get('briefTitle', ''),
                    'description': description.get('briefSummary', ''),
                    'status': study.get('protocolSection', {}).get('statusModule', {}).get('overallStatus', ''),
                    'eligibility': eligibility.get('eligibilityCriteria', ''),
                    'locations': self._extract_locations(contacts),
                    'url': f"https://clinicaltrials.gov/study/{identification.get('nctId', '')}"
                })
            
            return trials
            
        except Exception as e:
            print(f"Error searching clinical trials: {e}")
            return []
    
    def _extract_locations(self, contacts_module: Dict) -> List[str]:
        """Extract trial locations from contacts module"""
        locations = []
        for location in contacts_module.get('locations', []):
            city = location.get('city', '')
            state = location.get('state', '')
            country = location.get('country', '')
            if city or state:
                locations.append(f"{city}, {state}, {country}".strip(', '))
        return locations[:5]  # Limit to 5 locations