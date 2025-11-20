from typing import Dict, List, Any
import json
from datetime import datetime

class MemoryBank:
    """
    Long-term memory storage for patient diagnostic journeys
    """
    
    def __init__(self):
        self.storage = {}  # In production, use persistent storage
    
    def store_session(self, session_id: str, data: Dict) -> None:
        """Store session data"""
        if session_id not in self.storage:
            self.storage[session_id] = {
                'created_at': datetime.now().isoformat(),
                'history': []
            }
        
        self.storage[session_id]['history'].append({
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
    
    def retrieve_session(self, session_id: str) -> Dict:
        """Retrieve session data"""
        return self.storage.get(session_id, {})
    
    def get_symptom_evolution(self, session_id: str) -> List[Dict]:
        """Get how symptoms have evolved over time"""
        session = self.retrieve_session(session_id)
        return [
            entry['data'].get('symptoms', {})
            for entry in session.get('history', [])
            if 'symptoms' in entry['data']
        ]
    
    def get_search_history(self, session_id: str) -> List[str]:
        """Get history of conditions searched"""
        session = self.retrieve_session(session_id)
        conditions = []
        
        for entry in session.get('history', []):
            if 'conditions' in entry['data']:
                conditions.extend([
                    c.get('name', '') 
                    for c in entry['data']['conditions']
                ])
        
        return list(set(conditions))  # Unique conditions

class SessionManager:
    """Manages active sessions"""
    
    def __init__(self):
        self.active_sessions = {}
        self.memory_bank = MemoryBank()
    
    def create_session(self, session_id: str) -> Dict:
        """Create new session"""
        self.active_sessions[session_id] = {
            'created_at': datetime.now().isoformat(),
            'state': 'active',
            'current_step': 'symptom_collection'
        }
        return self.active_sessions[session_id]
    
    def update_session_state(self, session_id: str, state: str, data: Dict = None) -> None:
        """Update session state"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['state'] = state
            self.active_sessions[session_id]['last_updated'] = datetime.now().isoformat()
            
            if data:
                self.memory_bank.store_session(session_id, data)
    
    def get_session(self, session_id: str) -> Dict:
        """Get session data"""
        return self.active_sessions.get(session_id, {})