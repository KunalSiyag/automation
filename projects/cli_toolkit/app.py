from flask import Flask, request, jsonify
import os
from toolkit import CLIToolkit

app = Flask(__name__)
# Configure Flask to serve static files (like index.html) from the root directory
app.static_folder = '.'
app.static_url_path = '/'

toolkit = CLIToolkit()

@app.route('/')
def serve_index():
    """Serve the main web application page from the project root."""
    return app.send_static_file('index.html')

@app.route('/hash', methods=['POST'])
def hash_file_web():
    """Web endpoint to hash a file given its path on the server."""
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'Missing filename in request body'}), 400

    filename = data['filename']
    algorithm = data.get('algorithm', 'sha256')

    if not os.path.exists(filename):
        return jsonify({'error': f'File not found: {filename}'}), 404
    if not os.path.isfile(filename):
        return jsonify({'error': f'Path is not a file: {filename}'}), 400

    try:
        hash_value = toolkit.hash_file(filename, algorithm)
        return jsonify({'filename': filename, 'algorithm': algorithm, 'hash': hash_value})
    except ValueError as e:
        # e.g., unsupported hash algorithm
        return jsonify({'error': str(e)}), 400
    except IOError as e:
        # e.g., permission denied, file unreadable
        return jsonify({'error': f'File access error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
