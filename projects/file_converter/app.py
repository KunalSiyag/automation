import os
import uuid
from pathlib import Path
from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from converter import FileConverter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
app.secret_key = 'a_very_secret_key_for_flash_messages' # In a real app, use a strong, random key from env var

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
            flash("No file part was submitted.", "error")
            return redirect(url_for('index'))
        file = request.files['file']
        if file.filename == '':
            flash("No file was selected for upload.", "error")
            return redirect(url_for('index'))
        
        output_format = request.form.get('output_format')
        if not output_format or output_format not in converter.supported_formats:
            flash(f"Invalid or unsupported output format selected: {output_format}", "error")
            return redirect(url_for('index'))

        if file:
            original_filename = secure_filename(file.filename)
            # Use a unique UUID to prevent filename collisions
            unique_id = uuid.uuid4()
            input_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{original_filename}")
            file.save(input_file_path)

            input_format = converter.detect_format(input_file_path)
            if input_format not in converter.supported_formats:
                flash(f"Unsupported input file format: {input_format}", "error")
                return redirect(url_for('index'))

            output_filename = f"{Path(original_filename).stem}.{output_format}"
            output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{output_filename}")

            converter.convert(input_file_path, output_file_path)
            
            # Send the converted file for download
            # For successful downloads, a flash message is often not immediately seen, as the browser initiates download.
            # The success is implied by the download action itself.
            return send_file(output_file_path, as_attachment=True, download_name=output_filename)

    except NotImplementedError as e:
        flash(f"Conversion error: {e}. Only JSON and CSV conversions are currently implemented.", "error")
        return redirect(url_for('index'))
    except ValueError as e:
        flash(f"Conversion error: {e}", "error")
        return redirect(url_for('index'))
    except Exception as e:
        # Log the unexpected error for debugging purposes
        app.logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        flash(f"An unexpected error occurred during conversion: {e}", "error")
        return redirect(url_for('index'))
    finally:
        # Clean up uploaded and converted files
        if input_file_path and os.path.exists(input_file_path):
            os.remove(input_file_path)
        if output_file_path and os.path.exists(output_file_path):
            os.remove(output_file_path)
    
    flash("An unknown error occurred.", "error") # Should ideally not be reached
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
