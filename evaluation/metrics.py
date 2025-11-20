from typing import Dict, List
import json

class EvaluationMetrics:
    """Calculate evaluation metrics for RarePath AI"""
    
    @staticmethod
    def calculate_accuracy(test_results: List[Dict]) -> Dict:
        """Calculate diagnostic accuracy metrics"""
        
        total_tests = len(test_results)
        if total_tests == 0:
            return {}
        
        # Top-K accuracy
        top1_correct = sum(1 for r in test_results if r.get('evaluation', {}).get('condition_match'))
        top5_correct = sum(1 for r in test_results if len(r.get('evaluation', {}).get('found_conditions', [])) > 0)
        
        # Specialist accuracy
        specialist_correct = sum(1 for r in test_results if r.get('evaluation', {}).get('specialist_match'))
        
        # Average confidence
        all_confidences = []
        for r in test_results:
            all_confidences.extend(r.get('evaluation', {}).get('confidence_scores', []))
        
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
        
        return {
            'total_tests': total_tests,
            'top1_accuracy': top1_correct / total_tests,
            'top5_accuracy': top5_correct / total_tests,
            'specialist_accuracy': specialist_correct / total_tests,
            'average_confidence': avg_confidence,
            'success_rate': sum(1 for r in test_results if r.get('success')) / total_tests
        }
    
    @staticmethod
    def print_metrics_report(metrics: Dict):
        """Print formatted metrics report"""
        
        print("\n" + "=" * 80)
        print("EVALUATION METRICS REPORT")
        print("=" * 80)
        
        print(f"\nTotal Test Cases: {metrics.get('total_tests', 0)}")
        print(f"Success Rate: {metrics.get('success_rate', 0)*100:.1f}%")
        print(f"\nAccuracy Metrics:")
        print(f"  Top-1 Accuracy: {metrics.get('top1_accuracy', 0)*100:.1f}%")
        print(f"  Top-5 Accuracy: {metrics.get('top5_accuracy', 0)*100:.1f}%")
        print(f"  Specialist Match: {metrics.get('specialist_accuracy', 0)*100:.1f}%")
        print(f"\nConfidence Metrics:")
        print(f"  Average Confidence: {metrics.get('average_confidence', 0):.2f}")
        print("=" * 80)
