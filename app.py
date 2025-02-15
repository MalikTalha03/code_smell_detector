import json
from flask import Flask, render_template, request, jsonify, send_file, session
import os
from main import detect_code_smells_in_directory, analyze_code_snippet
from fpdf import FPDF

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 

# Set the secret key to sign session data
app.secret_key = 'smell_detector'

UPLOAD_FOLDER = 'uploaded_projects'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan_project():
    project_folder = request.form['projectFolder']
    print(f"Scanning project: {project_folder}")
    
    # Store project_folder in session
    session['project_folder'] = project_folder
    
    report_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{os.path.basename(project_folder)}_report.json')

    # Run the code smell detector
    detect_code_smells_in_directory(project_folder, report_path)

    # Load JSON report
    with open(report_path, 'r') as report_file:
        report_data = json.load(report_file)

    return jsonify(report_data)

from flask import Flask, request, jsonify

@app.route('/analyze_snippet', methods=['POST'])
def analyze_snippet():
    # Get the code snippet from the request
    code_snippet = request.form.get('codeSnippet', '')

    if not code_snippet:
        return jsonify({'error': 'No code snippet provided'}), 400

    try:
        # Placeholder: Analyze the code snippet
        results = analyze_code_snippet(code_snippet)  # Implement this function to detect code smells
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/analyze_file', methods=['POST'])
def analyze_file():
    # Check if a file is included in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    # Ensure the uploaded file is a Python file
    if not file.filename.endswith('.py'):
        return jsonify({'error': 'Only Python (.py) files are allowed'}), 400

    try:
        # Read the file contents
        file_content = file.read().decode('utf-8')

        # Placeholder: Analyze the file contents
        results = analyze_code_snippet(file_content)  # Reuse the same analysis function
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Abbreviations for code smells
ABBREVIATIONS = {
    "Long Parameter List": "LPL",
    "Long Base Class List": "LBCL",
    "Long Class": "LC",
    "Long Method": "LM",
    "Complex Container Comprehension": "CCC",
    "Long Lambda Function": "LLF",
    "Long Ternary Conditional Expression": "LTCE",
    "Long Scope Chaining": "LSC"
}


@app.route('/download_pdf', methods=['GET'])
def download_pdf():
    
    project_folder = session.get('project_folder')
    
    if not project_folder:
        return jsonify({"error": "Project folder not found in session"}), 400

    report_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{os.path.basename(project_folder)}_report.json')
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{os.path.basename(project_folder)}_report.pdf')

    # Load JSON report data
    try:
        with open(report_path, 'r') as report_file:
            report_data = json.load(report_file)
    except FileNotFoundError:
        return jsonify({"error": "Report not found for the given project folder"}), 404

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Code Smell Detection Report", ln=True, align="C")

    # Add Abbreviations Section
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Abbreviations", ln=True)
    pdf.set_font("Arial", "", 12)
    for full_form, abbrev in ABBREVIATIONS.items():
        pdf.cell(200, 8, f"{abbrev} = {full_form}", ln=True)

    # Add Table Header
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, "Code Smell", 1, 0, "C")
    pdf.cell(110, 10, "File Path", 1, 0, "C")
    pdf.cell(30, 10, "Line No", 1, 1, "C")

    # Add Table Rows
    pdf.set_font("Arial", "", 10)
    for item in report_data:
        # Get the full code smell name and find its abbreviation
        full_code_smell = item["code_smell"]
        code_smell_abbr = ""
        for full_form, abbrev in ABBREVIATIONS.items():
            if full_form in full_code_smell:
                code_smell_abbr = abbrev
                break

        pdf.cell(40, 10, code_smell_abbr, 1, 0, "C")  # Use abbreviation in the cell
        pdf.cell(110, 10, item["file"], 1, 0, "L")
        pdf.cell(30, 10, str(item["line_number"]), 1, 1, "C")

    # Save PDF
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=5007)
