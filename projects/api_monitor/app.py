from flask import Flask, render_template, jsonify
from monitor import APIMonitor
import logging
import threading
import time

# Configure basic logging for the Flask app
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app, specifying the current directory as the template folder
# This allows index.html to be at the project root as per requirements.
app = Flask(__name__, template_folder='.')
monitor = APIMonitor()

# Configuration for the background monitor interval (e.g., every 5 minutes)
MONITOR_INTERVAL_SECONDS = 300

# Add some initial endpoints to monitor, including custom timeouts for demonstration
monitor.add_endpoint('Google', 'https://www.google.com')
monitor.add_endpoint('GitHub API', 'https://api.github.com')
monitor.add_endpoint('Invalid URL (should fail)', 'http://invalid.url.example.com', timeout=2) # Shorter timeout for quicker failure
monitor.add_endpoint('Slow endpoint (should timeout)', 'https://httpbin.org/delay/6', timeout=3) # Endpoint designed to timeout

def _run_monitor_checks_continuously(monitor_instance):
    """
    Runs the APIMonitor's check_all method in a continuous loop
    with a specified interval. This is intended to be run in a
    separate daemon thread.
    """
    while True:
        logger.info(f"Background monitor: Running all endpoint checks...")
        try:
            monitor_instance.check_all()
            logger.info(f"Background monitor: Checks completed. Next check in {MONITOR_INTERVAL_SECONDS} seconds.")
        except Exception as e:
            logger.error(f"Background monitor: An error occurred during checks: {e}")
        time.sleep(MONITOR_INTERVAL_SECONDS)

@app.route('/')
def index():
    """Renders the main dashboard page."""
    logger.info("Serving index.html")
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_monitor_status():
    """Triggers a check of all endpoints and returns the latest results and aggregate statistics.
    Note: A background thread also continuously checks, but this provides an on-demand refresh.
    """
    logger.info("API /api/status called. Triggering an immediate endpoint check.")
    monitor.check_all() # Perform a check every time this API is called to ensure immediate feedback
    results = monitor.results # Get all accumulated results
    stats = monitor.get_stats()
    logger.debug(f"Returning API status: {len(results)} results, {stats.get('healthy', 0)} healthy.")
    return jsonify({
        'results': results,
        'stats': stats
    })

if __name__ == '__main__':
    logger.info("Starting Flask application.")

    # Start the background monitoring thread
    monitor_thread = threading.Thread(
        target=_run_monitor_checks_continuously,
        args=(monitor,),
        daemon=True # Daemon thread ensures it will exit when the main program exits
    )
    monitor_thread.start()
    logger.info(f"Background API monitor started, checking every {MONITOR_INTERVAL_SECONDS} seconds.")

    # Run the Flask app
    # In a production environment, use a WSGI server like Gunicorn or uWSGI
    app.run(debug=True, host='0.0.0.0', port=5000)
