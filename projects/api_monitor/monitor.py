"""
API Monitor - Monitor API endpoints and track their health
"""

import requests
import time
from datetime import datetime
from typing import List, Dict

class APIMonitor:
    def __init__(self):
        self.endpoints = []
        self.results = []
    
    def add_endpoint(self, name: str, url: str, method: str = 'GET'):
        self.endpoints.append({
            'name': name,
            'url': url,
            'method': method
        })
    
    def check_endpoint(self, endpoint: Dict) -> Dict:
        try:
            start_time = time.time()
            response = requests.request(
                method=endpoint['method'],
                url=endpoint['url'],
                timeout=10
            )
            response_time = (time.time() - start_time) * 1000
            
            return {
                'name': endpoint['name'],
                'url': endpoint['url'],
                'status': response.status_code,
                'response_time': round(response_time, 2),
                'healthy': 200 <= response.status_code < 300,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'name': endpoint['name'],
                'url': endpoint['url'],
                'status': 0,
                'response_time': 0,
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_all(self) -> List[Dict]:
        results = []
        for endpoint in self.endpoints:
            result = self.check_endpoint(endpoint)
            results.append(result)
            self.results.append(result)
        return results
    
    def get_stats(self) -> Dict:
        if not self.results:
            return {}
        
        healthy_count = sum(1 for r in self.results if r.get('healthy'))
        total_count = len(self.results)
        avg_response_time = sum(r.get('response_time', 0) for r in self.results) / total_count
        
        return {
            'total_checks': total_count,
            'healthy': healthy_count,
            'unhealthy': total_count - healthy_count,
            'uptime_percentage': (healthy_count / total_count) * 100 if total_count > 0 else 0,
            'avg_response_time': round(avg_response_time, 2)
        }

def main():
    monitor = APIMonitor()
    monitor.add_endpoint('Google', 'https://www.google.com')
    monitor.add_endpoint('GitHub API', 'https://api.github.com')
    
    print("🔍 Checking endpoints...")
    results = monitor.check_all()
    
    for result in results:
        status = "✅" if result['healthy'] else "❌"
        print(f"{status} {result['name']}: {result.get('response_time', 'N/A')}ms")
    
    stats = monitor.get_stats()
    print(f"
📊 Stats: {stats['uptime_percentage']:.1f}% uptime")

if __name__ == '__main__':
    main()
