from flask import Flask, render_template, jsonify
from monitor import APIMonitor
import logging

# Configure basic logging for the Flask app
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
monitor = APIMonitor()

# Add some initial endpoints to monitor, including custom timeouts for demonstration
monitor.add_endpoint('Google', 'https://www.google.com')
monitor.add_endpoint('GitHub API', 'https://api.github.com')
monitor.add_endpoint('Invalid URL (should fail)', 'http://invalid.url.example.com', timeout=2) # Shorter timeout for quicker failure
monitor.add_endpoint('Slow endpoint (should timeout)', 'https://httpbin.org/delay/6', timeout=3) # Endpoint designed to timeout

@app.route('/')
def index():
    """Renders the main dashboard page."""
    logger.info("Serving index.html")
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_monitor_status():
    """Triggers a check of all endpoints and returns the latest results and aggregate statistics."""
    logger.info("API /api/status called. Triggering all endpoint checks.")
    monitor.check_all() # Perform a check every time this API is called
    results = monitor.results # Get all accumulated results
    stats = monitor.get_stats()
    logger.debug(f"Returning API status: {len(results)} results, {stats.get('healthy', 0)} healthy.")
    return jsonify({
        'results': results,
        'stats': stats
    })

if __name__ == '__main__':
    logger.info("Starting Flask application.")
    # Run the Flask app
    # In a production environment, use a WSGI server like Gunicorn or uWSGI
    app.run(debug=True, host='0.0.0.0', port=5000)
