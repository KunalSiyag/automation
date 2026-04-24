import os
import uuid
from pathlib import Path
from flask import Flask, request, render_template, send_file, flash, redirect, url_for, after_this_request
from werkzeug.utils import secure_filename
from converter import FileConverter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload size
# Improved: Load secret key from environment variable for better security and deployability
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_default_secret_key_for_development_only')

converter = FileConverter()

@app.route('/')
def index():
    # Pass the supported formats to the template for dynamic display
    return render_template('index.html', supported_formats=sorted(converter.supported_formats))

@app.route('/convert', methods=['POST'])
def convert_file():
    input_file_path = None
    output_file_path = None
    files_to_clean = [] # List to track files created in this request for deferred cleanup

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
            files_to_clean.append(input_file_path) # Mark input file for cleanup

            input_format = converter.detect_format(input_file_path)
            if input_format not in converter.supported_formats:
                flash(f"Unsupported input file format: {input_format}", "error")
                return redirect(url_for('index'))

            output_filename = f"{Path(original_filename).stem}.{output_format}"
            output_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{output_filename}")
            
            converter.convert(input_file_path, output_file_path)
            files_to_clean.append(output_file_path) # Mark output file for cleanup

            @after_this_request
            def remove_temporary_files(response):
                for f_path in files_to_clean:
                    if os.path.exists(f_path):
                        try:
                            os.remove(f_path)
                            app.logger.info(f"Successfully cleaned up temporary file: {f_path}")
                        except OSError as e:
                            app.logger.error(f"Error cleaning up temporary file {f_path}: {e}")
                return response
            
            # Send the converted file for download
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
        # This block ensures cleanup even if an error prevents after_this_request from running.
        # It will only clean files that still exist (e.g., if after_this_request didn't run or an error occurred before it registered).
        for f_path in files_to_clean:
            if os.path.exists(f_path):
                try:
                    os.remove(f_path)
                    app.logger.info(f"Cleaned up residual temporary file in finally block: {f_path}")
                except OSError as e:
                    app.logger.error(f"Error cleaning up residual temporary file {f_path} in finally block: {e}")
    
    flash("An unknown error occurred.", "error") # Should ideally not be reached
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
