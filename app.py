from flask import Flask, request, render_template, jsonify
import os
import subprocess

app = Flask(__name__)

# Set the upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        error = "No file was selected"
        return render_template("index.html", error=error)

    file = request.files['file']

    if file.filename == '':
        error = "No file was selected"
        return render_template("index.html", error=error)

    if file and allowed_file(file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Get printing settings from the form
        copies = request.form.get('copies', '1')
        page_range = request.form.get('page_range', '')
        orientation = request.form.get('orientation', 'portrait')
        paper_size = request.form.get('paper_size', 'A4')

        # Print the file with the specified settings
        try:
            print_file(filepath, copies, page_range, orientation, paper_size)
            done = "File uploaded and printed successfully!"
            return render_template("index.html", done=done)
        except Exception as e:
            error = f"Failed to print file: {str(e)}"
            return render_template("index.html", error=error)
    else:
        error = "File type not allowed"
        return render_template("index.html", error=error)

def print_file(filepath, copies, page_range, orientation, paper_size):
    # Build the `lp` command with the specified settings
    command = ['lp', filepath]

    # Add options for copies
    if copies and int(copies) > 1:
        command.extend(['-n', copies])

    # Add options for page range
    if page_range:
        command.extend(['-o', f'page-ranges={page_range}'])

    # Add options for orientation
    if orientation == 'landscape':
        command.extend(['-o', 'orientation-requested=4'])  # 4 = landscape

    # Add options for paper size
    if paper_size:
        command.extend(['-o', f'media={paper_size}'])

    # Execute the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"Printing failed: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)