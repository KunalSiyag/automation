from flask import Flask, render_template
import os
import logging

# Configure Flask to look for index.html in the project root and static files in a 'static' folder.
app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)), static_folder='static')

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index() -> str:
    # Input validation enhanced
    """Serve the main Tic-Tac-Toe game page."""
    app.logger.info('Serving index.html')
    return render_template('index.html')

if __name__ == '__main__':
    # This block allows running the Flask app directly for development purposes.
    # In a production environment, a WSGI server (like Gunicorn) would typically be used.
    app.run(debug=True)
