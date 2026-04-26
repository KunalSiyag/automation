from flask import Flask, request, jsonify
import os
from toolkit import CLIToolkit

app = Flask(__name__)
# Configure Flask to serve static files (like index.html) from the root directory
app.static_folder = '.'
app.static_url_path = '/' # This maps requests to '/' (root) to the static_folder

toolkit = CLIToolkit()

# Define a base directory for safe file operations
# This restricts all file access to within the application's root directory.
# Using abspath + dirname(__file__) ensures it's relative to the script's location.
SAFE_FILE_DIR = os.path.abspath(os.path.dirname(__file__))

def is_path_safe(requested_path: str, safe_base_dir: str) -> bool:
    """Checks if a requested path is safely contained within the base directory.

    This function prevents directory traversal attacks by ensuring that the
    absolute and normalized path of the requested file is a sub-path of the
    specified safe base directory.
    """
    # Get absolute and normalized paths for robust comparison
    abs_requested_path = os.path.abspath(requested_path)
    abs_base_dir = os.path.abspath(safe_base_dir)

    # Use os.path.commonprefix to check if abs_requested_path starts with abs_base_dir.
    # This is a robust way to prevent directory traversal. For example, if
    # abs_base_dir is /app and requested_path is /app/../etc/passwd, 
    # abs_requested_path would resolve to /etc/passwd and commonprefix would be /,
    # which is not equal to /app.
    return os.path.commonprefix([abs_requested_path, abs_base_dir]) == abs_base_dir

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

    filename_raw = data['filename']
    algorithm = data.get('algorithm', 'sha256')

    try:
        # Resolve the real path to handle symlinks and path normalization
        filename_resolved = os.path.realpath(filename_raw)

        # Security check: Ensure the resolved path is within the allowed directory
        if not is_path_safe(filename_resolved, SAFE_FILE_DIR):
            return jsonify({'error': 'Access denied: Path outside allowed directory'}), 403

        if not os.path.exists(filename_resolved):
            return jsonify({'error': f'File not found: {filename_raw}'}), 404
        if not os.path.isfile(filename_resolved):
            return jsonify({'error': f'Path is not a file: {filename_raw}'}), 400

        hash_value = toolkit.hash_file(filename_resolved, algorithm)
        return jsonify({'filename': filename_raw, 'algorithm': algorithm, 'hash': hash_value})
    except ValueError as e:
        # e.g., unsupported hash algorithm
        return jsonify({'error': str(e)}), 400
    except IOError as e:
        # e.g., permission denied, file unreadable
        return jsonify({'error': f'File access error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

@app.route('/file-info', methods=['POST'])
def file_info_web():
    """Web endpoint to get information about a file or path on the server."""
    data = request.get_json()
    if not data or 'path' not in data:
        return jsonify({'error': 'Missing path in request body'}), 400

    path_to_check_raw = data['path']

    try:
        # Get absolute and canonical paths for comprehensive safety checks and detailed response
        absolute_path = os.path.abspath(path_to_check_raw)
        canonical_path = os.path.realpath(path_to_check_raw)

        # Security check: Ensure both the absolute path (as given)
        # and the canonical path (after resolving symlinks) are within the allowed directory.
        # This prevents symlink traversal attacks.
        if not is_path_safe(absolute_path, SAFE_FILE_DIR):
            return jsonify({'error': 'Access denied: Path (absolute) outside allowed directory'}), 403
        if not is_path_safe(canonical_path, SAFE_FILE_DIR):
            return jsonify({'error': 'Access denied: Path (canonical/resolved) outside allowed directory'}), 403

        # Call toolkit.file_info which provides basic info like is_file and size
        info = toolkit.file_info(path_to_check_raw)

        # Augment the info with additional, robust path details
        info['requested_path'] = path_to_check_raw
        info['exists'] = os.path.exists(path_to_check_raw)
        info['is_directory'] = os.path.isdir(path_to_check_raw)
        info['is_symlink'] = os.path.islink(path_to_check_raw)
        info['absolute_path'] = absolute_path
        info['canonical_path'] = canonical_path # The path after resolving all symlinks

        return jsonify(info)
    except Exception as e:
        # file_info is designed to be robust even for non-existent paths,
        # but catch any truly unexpected issues.
        return jsonify({'error': f'An unexpected error occurred while getting info for {path_to_check_raw}: {str(e)}'}), 500

@app.route('/count-lines', methods=['POST'])
def count_lines_web():
    """Web endpoint to count lines in a file."""
    data = request.get_json()
    if not data or 'path' not in data:
        return jsonify({'error': 'Missing path in request body'}), 400

    filepath_raw = data['path']

    try:
        # Resolve the real path to handle symlinks and path normalization
        filepath_resolved = os.path.realpath(filepath_raw)

        # Security check: Ensure the resolved path is within the allowed directory
        if not is_path_safe(filepath_resolved, SAFE_FILE_DIR):
            return jsonify({'error': 'Access denied: Path outside allowed directory'}), 403

        if not os.path.exists(filepath_resolved):
            return jsonify({'error': f'File not found: {filepath_raw}'}), 404
        if not os.path.isfile(filepath_resolved):
            return jsonify({'error': f'Path is not a file: {filepath_raw}'}), 400

        line_counts = toolkit.count_lines(filepath_resolved)
        return jsonify(line_counts)
    except IOError as e:
        return jsonify({'error': f'File access error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    # In a production environment, debug=False and use a production WSGI server.
    app.run(debug=True, port=5000)
