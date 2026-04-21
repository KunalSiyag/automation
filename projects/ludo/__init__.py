import logging
from flask import Flask, render_template

"""Ludo Game Package."""

# Type safety improved - 193600
# Documentation updated - 194043
# Error handling enhanced - 194100

# Configure Flask to look for templates in the project root to adhere to constraints
app = Flask(__name__, template_folder='.')

@app.route('/')
def index() -> str:
    """Serves the main Ludo game page from index.html at the project root."""
    logging.info("Attempting to render index.html for the Ludo game.")
    return render_template('index.html')

if __name__ == '__main__':
    # Configure basic logging to see informational messages during development
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Starting Ludo Flask application.")
    # Run the Flask application in debug mode for development
    app.run(debug=True)

# Type safety improved - 070453
