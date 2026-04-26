import requests
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class APIMonitor:
    def __init__(self):
        self.endpoints = []
        self.results = [] # Stores the latest check result for each endpoint
        self.history = {} # Optional: to store historical results if needed for trends

    def add_endpoint(self, name, url, method='GET', timeout=10, data=None, headers=None):
        """Adds an endpoint to be monitored."""
        self.endpoints.append({
            'name': name,
            'url': url,
            'method': method,
            'timeout': timeout,
            'data': data,
            'headers': headers
        })
        logger.info(f"Added endpoint: {name} - {url}")

    def check_endpoint(self, endpoint):
        """
        Performs an HTTP check on a single endpoint and returns the result.
        Now includes status_code and error_message for more detail.
        """
        url = endpoint['url']
        name = endpoint['name']
        method = endpoint.get('method', 'GET')
        timeout = endpoint.get('timeout', 10) # Default timeout in seconds
        data = endpoint.get('data') # For POST requests
        headers = endpoint.get('headers')

        start_time = time.monotonic()
        healthy = False
        status_code = None
        error_message = None

        try:
            response = requests.request(method, url, timeout=timeout, data=data, headers=headers)
            response.raise_for_status() # Raise an exception for HTTP error codes (4xx or 5xx)
            healthy = True
            status_code = response.status_code
        except requests.exceptions.Timeout:
            error_message = f"Timeout after {timeout} seconds."
            logger.warning(f"Endpoint '{name}' timed out after {timeout}s: {url}")
        except requests.exceptions.ConnectionError as e:
            error_message = f"Connection error: {e}"
            logger.warning(f"Endpoint '{name}' connection error: {url} - {e}")
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            error_message = f"HTTP error: {status_code} {e.response.reason}" if e.response and e.response.reason else f"HTTP error: {e}"
            logger.warning(f"Endpoint '{name}' HTTP error: {url} - {error_message}")
        except requests.exceptions.RequestException as e:
            # Catch all other requests-related exceptions
            error_message = f"Request failed: {e}"
            logger.error(f"Endpoint '{name}' general request error: {url} - {e}")
        except Exception as e:
            # Catch any other unexpected errors
            error_message = f"Unexpected error: {e}"
            logger.critical(f"Endpoint '{name}' unexpected error during check: {url} - {e}")
        finally:
            end_time = time.monotonic()
            response_time = round((end_time - start_time) * 1000) # in ms

        result = {
            'name': name,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'healthy': healthy,
            'status_code': status_code, # Add status code
            'response_time': response_time,
            'error_message': error_message # Add error message
        }
        return result

    def check_all(self):
        """
        Checks all configured endpoints and updates the internal results.
        This method is called by the background thread.
        """
        logger.debug(f"Initiating checks for {len(self.endpoints)} endpoints.")
        current_results = []
        for endpoint in self.endpoints:
            try:
                result = self.check_endpoint(endpoint)
                current_results.append(result)
                logger.debug(f"Checked '{endpoint['name']}': Healthy={result['healthy']}, Status={result['status_code']}, Time={result['response_time']}ms")
            except Exception as e:
                logger.error(f"Error checking endpoint {endpoint['name']}: {e}")
                # Append a failure result if check_endpoint itself fails unexpectedly
                current_results.append({
                    'name': endpoint['name'],
                    'url': endpoint['url'],
                    'timestamp': datetime.now().isoformat(),
                    'healthy': False,
                    'status_code': None,
                    'response_time': 0, # Cannot determine response time if check_endpoint fails
                    'error_message': f"Internal monitor error: {e}"
                })
        self.results = current_results
        logger.debug(f"Finished checking all endpoints. {len(self.results)} results collected.")

    def get_stats(self):
        """Calculates and returns aggregate statistics based on the latest results."""
        total_checks = len(self.results)
        healthy_checks = sum(1 for r in self.results if r['healthy'])
        unhealthy_checks = total_checks - healthy_checks
        
        uptime_percentage = (healthy_checks / total_checks * 100) if total_checks > 0 else 0
        
        avg_response_time = 0
        if healthy_checks > 0:
            total_response_time = sum(r['response_time'] for r in self.results if r['healthy'] and r['response_time'] is not None)
            avg_response_time = round(total_response_time / healthy_checks)

        return {
            'total_checks': total_checks,
            'healthy': healthy_checks,
            'unhealthy': unhealthy_checks,
            'uptime_percentage': round(uptime_percentage, 2),
            'avg_response_time_ms': avg_response_time
        }
