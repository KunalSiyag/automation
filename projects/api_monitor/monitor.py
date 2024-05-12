import requests
import time
import logging

# Configure logging for the monitor module
logger = logging.getLogger(__name__)
# Ensure a handler is configured if the root logger isn't already set up by the main app.
# In this project, app.py configures basicConfig, so this check mostly for standalone use.
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class APIMonitor:
    def __init__(self):
        self.endpoints = []
        self.results = [] # Stores the results of the last check_all operation
        logger.info("APIMonitor initialized.")

    def add_endpoint(self, name, url, method='GET', timeout=5):
        """Adds an endpoint to monitor with an optional custom timeout."""
        if not url.startswith(('http://', 'https://')):
            logger.warning(f"Attempted to add endpoint '{name}' with an invalid URL scheme: {url}. Must be http(s).")
            # For robustness, could raise ValueError or return False. Sticking to logging for 'safe, incremental'.
        self.endpoints.append({'name': name, 'url': url, 'method': method, 'timeout': timeout})
        logger.info(f"Added endpoint: '{name}' ({url}) with default/custom timeout of {timeout}s.")

    def check_endpoint(self, endpoint):
        """Checks a single endpoint for health and response time, handling various network errors."""
        start_time = time.monotonic()
        healthy = False
        status_code = None
        error_message = None
        response_time = 0
        request_timeout = endpoint.get('timeout', 5) # Use endpoint-specific timeout, default to 5s

        logger.debug(f"Checking endpoint: '{endpoint['name']}' ({endpoint['url']}) with timeout {request_timeout}s")
        try:
            response = requests.request(
                endpoint['method'],
                endpoint['url'],
                timeout=request_timeout
            )
            response_time = (time.monotonic() - start_time) * 1000 # milliseconds
            healthy = response.status_code < 400 # HTTP status codes below 400 are generally considered healthy
            status_code = response.status_code

            if healthy:
                logger.info(f"Endpoint '{endpoint['name']}' ({endpoint['url']}) is HEALTHY. Status: {status_code}, Time: {response_time:.2f}ms")
            else:
                logger.warning(f"Endpoint '{endpoint['name']}' ({endpoint['url']}) is UNHEALTHY. Status: {status_code}, Time: {response_time:.2f}ms")

        except requests.exceptions.Timeout:
            response_time = (time.monotonic() - start_time) * 1000 # ms
            healthy = False
            error_message = f"Request timed out after {request_timeout}s."
            logger.error(f"Endpoint '{endpoint['name']}' ({endpoint['url']}) timed out. Error: {error_message}")
        except requests.exceptions.ConnectionError as e:
            response_time = (time.monotonic() - start_time) * 1000 # ms
            healthy = False
            error_message = f"Connection error: {e}"
            logger.error(f"Endpoint '{endpoint['name']}' ({endpoint['url']}) encountered a connection error. Error: {error_message}")
        except requests.exceptions.RequestException as e:
            response_time = (time.monotonic() - start_time) * 1000 # ms
            healthy = False
            error_message = f"An unexpected request error occurred: {e}"
            logger.error(f"Endpoint '{endpoint['name']}' ({endpoint['url']}) encountered an unexpected request error. Error: {error_message}")
        except Exception as e:
            response_time = (time.monotonic() - start_time) * 1000 # ms
            healthy = False
            error_message = f"An unknown error occurred: {e}"
            logger.exception(f"Endpoint '{endpoint['name']}' ({endpoint['url']}) encountered an unknown error (full traceback below).")

        result = {
            'endpoint_name': endpoint['name'],
            'url': endpoint['url'],
            'healthy': healthy,
            'status': status_code,
            'response_time': response_time,
            'timestamp': time.time(),
            'error': error_message
        }
        return result

    def check_all(self):
        """Checks all configured endpoints and updates the internal results."""
        logger.info(f"Starting check for all {len(self.endpoints)} endpoints.")
        current_results = []
        for endpoint in self.endpoints:
            result = self.check_endpoint(endpoint)
            current_results.append(result)
        self.results = current_results # Update the monitor's results attribute with the latest batch
        logger.info(f"Finished checking all {len(self.endpoints)} endpoints.")

    def get_stats(self):
        """Calculates aggregate statistics based on the latest monitoring results."""
        total_checks = len(self.results)
        healthy_checks = sum(1 for r in self.results if r['healthy'])
        # Handle division by zero for uptime_percentage if no checks have been performed
        uptime_percentage = (healthy_checks / total_checks * 100) if total_checks > 0 else 0
        logger.debug(f"Calculated stats: Total={total_checks}, Healthy={healthy_checks}, Uptime={uptime_percentage:.2f}%")
        return {
            'total_checks': total_checks,
            'healthy': healthy_checks,
            'unhealthy': total_checks - healthy_checks,
            'uptime_percentage': uptime_percentage
        }
