import os
import zipfile
from flask import Flask, render_template, request, redirect, send_file
from werkzeug.utils import secure_filename
import subprocess
import shutil

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CODER_OUTPUT = 'coder_output'
FORMATTER_OUTPUT = 'formatter_output'
FINAL_ZIP = 'final_output.zip'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CODER_OUTPUT'] = CODER_OUTPUT
app.config['FORMATTER_OUTPUT'] = FORMATTER_OUTPUT

# Ensure these paths are correct based on your actual directory structure
CODER_SCRIPT_PATH = os.path.join(os.getcwd(), 'coder.py')
FORMATTER_SCRIPT_PATH = os.path.join(os.getcwd(), 'formatter.py')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CODER_OUTPUT, exist_ok=True)
os.makedirs(FORMATTER_OUTPUT, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and file.filename.endswith('.zip'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Create a folder to unzip files into
        unzip_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'Unzipped')
        os.makedirs(unzip_folder, exist_ok=True)
        
        # Unzip the uploaded file into the 'Unzipped' folder
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(unzip_folder)
        
        # Flatten the unzipped folder structure
        for root, dirs, files in os.walk(unzip_folder):
            for file in files:
                file_path = os.path.join(root, file)
                dest_path = os.path.join(unzip_folder, file)
                os.rename(file_path, dest_path)

        # Remove subfolders
        for root, dirs, files in os.walk(unzip_folder, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                os.rmdir(dir_path)
        
        # Run coder.py on the 'Unzipped' folder
        subprocess.run(['python', CODER_SCRIPT_PATH, unzip_folder, app.config['CODER_OUTPUT']])

        
        # Run formatter.py on the output of coder.py
        subprocess.run(['python', FORMATTER_SCRIPT_PATH, app.config['CODER_OUTPUT'], app.config['FORMATTER_OUTPUT']])
        
        # Create a final ZIP file with the formatted output
        final_zip_path = os.path.join(app.config['UPLOAD_FOLDER'], FINAL_ZIP)
        with zipfile.ZipFile(final_zip_path, 'w') as zipf:
            for root, dirs, files in os.walk(app.config['FORMATTER_OUTPUT']):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), app.config['FORMATTER_OUTPUT']))
        
        # Delete the unzipped folder and its contents
        shutil.rmtree(unzip_folder)
        
        # Delete the coder output folder and its contents
        shutil.rmtree(app.config['CODER_OUTPUT'])

        # Delete the formatter output folder and its contents
        shutil.rmtree(app.config['FORMATTER_OUTPUT'])
        
        return send_file(final_zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)