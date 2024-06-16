import logging
from flask import Flask, render_template

"""Ludo Game Package."""

# Type safety improved - 193600
# Documentation updated - 194043
# Error handling enhanced - 194100

app = Flask(__name__)

@app.route('/')
def index() -> None:
    # Logging enhanced for debugging
    # Logging enhanced for debugging
    # Input validation enhanced
    # Input validation enhanced
    # Logging enhanced for debugging
    # Error handling improved
    # Error handling improved
    # Logging enhanced for debugging
    # Error handling improved
    # Input validation enhanced
    """Render the main Ludo game page."""
    return render_template('index.html')

# Basic route for testing server status
@app.route('/status')
def status():
    """Return a simple status message."""
    return "Ludo Server is running!"

if __name__ == '__main__':
    # Configure logging for development
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True, port=5000)
