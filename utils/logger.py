
import logging
from datetime import datetime
from typing import Dict, Any
import json

class RarePathLogger:
    """Custom logger for RarePath AI with observability"""
    
    def __init__(self, name: str = "rarepath"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler('rarepath.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        # Metrics storage
        self.metrics = {
            'agent_calls': {},
            'api_calls': {},
            'errors': [],
            'response_times': []
        }
    
    def log_agent_call(self, agent_name: str, action: str, data: Dict = None):
        """Log agent activity"""
        self.logger.info(f"Agent: {agent_name} | Action: {action}")
        
        if agent_name not in self.metrics['agent_calls']:
            self.metrics['agent_calls'][agent_name] = 0
        self.metrics['agent_calls'][agent_name] += 1
        
        if data:
            self.logger.debug(f"Data: {json.dumps(data, indent=2)}")
    
    def log_api_call(self, api_name: str, endpoint: str, response_time: float):
        """Log API calls"""
        self.logger.info(f"API: {api_name} | Endpoint: {endpoint} | Time: {response_time:.2f}s")
        
        if api_name not in self.metrics['api_calls']:
            self.metrics['api_calls'][api_name] = []
        
        self.metrics['api_calls'][api_name].append(response_time)
        self.metrics['response_times'].append(response_time)
    
    def log_error(self, error: Exception, context: str = ""):
        """Log errors"""
        self.logger.error(f"Error in {context}: {str(error)}", exc_info=True)
        self.metrics['errors'].append({
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'error': str(error)
        })
    
    def get_metrics(self) -> Dict:
        """Get aggregated metrics"""
        avg_response_time = (
            sum(self.metrics['response_times']) / len(self.metrics['response_times'])
            if self.metrics['response_times'] else 0
        )
        
        return {
            'total_agent_calls': sum(self.metrics['agent_calls'].values()),
            'agent_breakdown': self.metrics['agent_calls'],
            'total_api_calls': sum(len(v) for v in self.metrics['api_calls'].values()),
            'avg_response_time': avg_response_time,
            'total_errors': len(self.metrics['errors'])
        }
    
    def print_summary(self):
        """Print execution summary"""
        metrics = self.get_metrics()
        
        print("\n" + "=" * 60)
        print("EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Total Agent Calls: {metrics['total_agent_calls']}")
        print(f"Total API Calls: {metrics['total_api_calls']}")
        print(f"Average Response Time: {metrics['avg_response_time']:.2f}s")
        print(f"Total Errors: {metrics['total_errors']}")
        print("\nAgent Breakdown:")
        for agent, count in metrics['agent_breakdown'].items():
            print(f"  {agent}: {count} calls")
        print("=" * 60)