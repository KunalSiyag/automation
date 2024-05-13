import os
import uuid
from pathlib import Path
from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from converter import FileConverter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size

converter = FileConverter()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_file():
    input_file_path = None
    output_file_path = None

    try:
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
        
        output_format = request.form.get('output_format')
        if not output_format or output_format not in converter.supported_formats:
            return f"Invalid or unsupported output format selected: {output_format}", 400

        if file:
            original_filename = secure_filename(file.filename)
            # Use a unique UUID to prevent filename collisions
            unique_id = uuid.uuid4()
            input_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{original_filename}")
            file.save(input_file_path)

            input_format = converter.detect_format(input_file_path)
            if input_format not in converter.supported_formats:
                return f"Unsupported input file format: {input_format}", 400

            output_filename = f"{Path(original_filename).stem}.{output_format}"
            output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{output_filename}")

            converter.convert(input_file_path, output_file_path)
            
            # Send the converted file for download
            return send_file(output_file_path, as_attachment=True, download_name=output_filename)

    except NotImplementedError as e:
        return f"Conversion error: {e}. Only JSON and CSV conversions are currently implemented.", 501
    except ValueError as e:
        return f"Conversion error: {e}", 400
    except Exception as e:
        # Log the unexpected error for debugging purposes
        app.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return f"An unexpected error occurred during conversion: {e}", 500
    finally:
        # Clean up uploaded and converted files
        if input_file_path and os.path.exists(input_file_path):
            os.remove(input_file_path)
        if output_file_path and os.path.exists(output_file_path):
            os.remove(output_file_path)
    
    return "Something went wrong", 500 # Should ideally not be reached

if __name__ == '__main__':
    app.run(debug=True)
