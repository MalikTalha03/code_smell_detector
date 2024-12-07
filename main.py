from detector import *
import os
import ast
import json

def analyze_file(file_path, smells):
    """Analyze a Python file for code smells."""
    try:
        with open(file_path, 'r') as file:
            source_code = file.read()
            tree = ast.parse(source_code, filename=file_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                detect_lpl(node, smells, file_path)
                detect_lm(node, smells, file_path, source_code)
                detect_lsc(node, smells, file_path)
                
            if isinstance(node, ast.Lambda):
                detect_llf(node, smells, file_path, source_code)
                
            if isinstance(node, ast.IfExp):
                detect_ltce(node, smells, file_path, source_code)

            if isinstance(node, ast.ClassDef):
                detect_lc(node, smells, file_path, source_code)
                detect_lbcl(node, smells, file_path)

            if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp,ast.GeneratorExp)):
                detect_ccc(node, smells, file_path, source_code)
                
            # MNC and LMC not implemented
                
    except SyntaxError as e:
        print(f"Skipping file {file_path} due to syntax error: {e}")
    except Exception as e:
        print(f"Error analyzing file {file_path}: {e}")
        

def detect_code_smells_in_directory(directory_path, report_path):
    """Scan a directory for Python files and detect code smells."""
    smells = []
    print(f"Scanning directory: {directory_path}")
    print(f"Saving report to: {report_path}")
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                analyze_file(file_path, smells)
    # analyze_file('test.py', smells)
    with open(report_path, 'w') as report_file:
        json.dump(smells, report_file, indent=4)
    print(f"Code smells detected and saved to {report_path}")
    
def analyze_code_snippet(code_snippet, file_path="code_snippet.py"):
    """Analyze a code snippet for code smells."""
    try:
        smells = []
        source_code = code_snippet
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                detect_lpl(node, smells, file_path)
                detect_lm(node, smells, file_path, source_code)
                detect_lsc(node, smells, file_path)
                
            if isinstance(node, ast.Lambda):
                detect_llf(node, smells, file_path, source_code)
                
            if isinstance(node, ast.IfExp):
                detect_ltce(node, smells, file_path, source_code)

            if isinstance(node, ast.ClassDef):
                detect_lc(node, smells, file_path, source_code)
                detect_lbcl(node, smells, file_path)

            if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp,ast.GeneratorExp)):
                detect_ccc(node, smells, file_path, source_code)
                
            # MNC and LMC not implemented
        return smells
    except SyntaxError as e:
        print(f"Skipping file {file_path} due to syntax error: {e}")
    except Exception as e:
        print(f"Error analyzing file {file_path}: {e}")
                



# Example usage
if __name__ == "__main__":
    directory_path = "django"  # Replace with your Python directory path
    report_path = "dj_new.json"  # Replace with your desired output path
    detect_code_smells_in_directory(directory_path, report_path)