from flask import Flask, render_template, jsonify
from monitor import APIMonitor

app = Flask(__name__)
monitor = APIMonitor()

# Add some initial endpoints to monitor
monitor.add_endpoint('Google', 'https://www.google.com')
monitor.add_endpoint('GitHub API', 'https://api.github.com')
monitor.add_endpoint('Invalid URL (should fail)', 'http://invalid.url.example.com')

@app.route('/')
def index():
    """Renders the main dashboard page."""
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_monitor_status():
    """Triggers a check of all endpoints and returns the latest results and aggregate statistics."""
    monitor.check_all() # Perform a check every time this API is called
    results = monitor.results # Get all accumulated results
    stats = monitor.get_stats()
    return jsonify({
        'results': results,
        'stats': stats
    })

if __name__ == '__main__':
    # Run the Flask app
    # In a production environment, use a WSGI server like Gunicorn or uWSGI
    app.run(debug=True, host='0.0.0.0', port=5000)
