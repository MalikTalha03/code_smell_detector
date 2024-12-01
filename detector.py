import os
import ast
import json
from calculate import *
# Define thresholds for each code smell based on the provided metrics
THRESHOLDS = {
    "PAR_LPL": 5,    # Long Parameter List (LPL)
    "MLOC_LM": 38,  # Method/Function Lines of Code (LM)
    "DOC_LSC": 3,    # Depth of Closure (LSC)
    "CLOC_LC": 29,  # Class Lines of Code (LC)
    "LMC": 5,    # Length of Message Chain (LMC)
    "NBC_LBCL": 3,    # Number of Base Classes (LBCL)
    "NOC_LLF": 48,   # Number of Characters (LLF, LTCE)
    "PAR_LLF": 3,   # Number of Parameters for LLF
    "NOO_LLF": 8,    # Number of Operators and Operands (LLF)
    "NOL_LTCE": 3,    # Number of Lines (LTCE)
    "NOC_LTCE": 54,  # Number of Characters for LTCE
    "NOO_CCC": 8,    # Number of Operators/Operands in CCC
    "NOC_CCC": 3,    # Number of Comprehensions in CCC
    "NOFF_CCC": 3,   # Number of For Clauses and Filters in CCC
    "LEC_MNC": 3,    # Length of Element Chain (MNC)
    "DNC_MNC": 3,    # Depth of Nested Container (MNC)
    "NCT_MNC": 2,    # Number of Container Types (MNC)
}

def add_smell(smells, name, lineno, details, file_path):
    """Add a code smell to the list."""
    smells.append({
        "file": file_path,
        "code_smell": name,
        "line_number": lineno,
        "details": details
    })



# Detection functions for each smell
def detect_lpl(node, smells, file_path):
    """Detect Long Parameter List (LPL)."""
    par_count = calculate_par(node)
    if par_count > THRESHOLDS["PAR_LPL"]:
        add_smell(smells, "Long Parameter List (LPL)", node.lineno, f"Parameters: {par_count}", file_path)

def detect_lm(node, smells, file_path, source_code):
    """Detect Long Method (LM)."""
    mloc = calculate_mloc(node,source_code)
    if mloc > THRESHOLDS["MLOC_LM"]:
        add_smell(smells, "Long Method (LM)", node.lineno, f"Method Length: {mloc}", file_path)

def detect_lsc(node, smells, file_path):
    """Detect Long Scope Chaining (LSC)."""
    doc = calculate_doc(node)
    if doc > THRESHOLDS["DOC_LSC"]:
        add_smell(smells, "Long Scope Chaining (LSC)", node.lineno, f"Nested Levels: {doc}", file_path)

def detect_lc(node, smells, file_path,source_code):
    """Detect Large Class (LC)."""
    s_code = source_code
    cloc = calculate_cloc(node, s_code)
    if cloc > THRESHOLDS["CLOC_LC"]:
        add_smell(smells, "Large Class (LC)", node.lineno, f"Class Lines of Code: {cloc}", file_path)

def detect_lbcl(node, smells, file_path):
    """Detect Long Base Class List (LBCL)."""
    nbc = calculate_nbc(node)
    if nbc > THRESHOLDS["NBC_LBCL"]:
        add_smell(smells, "Long Base Class List (LBCL)", node.lineno, f"Base Classes: {nbc}", file_path)

def detect_llf(node, smells, file_path, source_code):
    """Detect Long Lambda Function (LLF)."""
    s_code = source_code.split("\n")
    noc = calculate_noc(node, s_code)
    par_ll = calculate_par(node)
    noo = calculate_noo(node)
    if noc > THRESHOLDS["NOC_LLF"]:
        if par_ll > THRESHOLDS["PAR_LLF"] or noo > THRESHOLDS["NOO_LLF"]:
            add_smell(smells, "Long Lambda Function (LLF)", node.lineno, f"Parameters: {par_ll}, Operators/Operands: {noo}", file_path)

def detect_ltce(node, smells, file_path, source_code):
    """Detect Long Ternary Conditional Expression (LTCE)."""
    nol = calculate_nol(node)
    s_code = source_code.split("\n")
    noc = calculate_noc(node, s_code)
    if nol > THRESHOLDS["NOC_LTCE"] or noc > THRESHOLDS["NOL_LTCE"]:
        add_smell(smells, "Long Ternary Conditional Expression (LTCE)", node.lineno, f"Expression Length: {nol}", file_path)

def detect_ccc(node, smells, file_path,source_code):
    """Detect Complex Container Comprehension (CCC)."""
    s_code = source_code.split("\n")
    noc = calculate_noc(node, s_code)
    noff = calculate_noff(node)
    noo = calculate_noo(node)
    if (noc > THRESHOLDS["NOC_CCC"] and noo > THRESHOLDS["NOO_CCC"]) or noff > THRESHOLDS["NOFF_CCC"]:
        add_smell(smells, "Complex Container Comprehension (CCC)", node.lineno, f"Operators/Operands: {noo}, For Clauses: {noff}", file_path)

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
    # for root, _, files in os.walk(directory_path):
    #     for file in files:
    #         if file.endswith(".py"):
    #             file_path = os.path.join(root, file)
    #             analyze_file(file_path, smells)
    analyze_file('test.py', smells)
    with open(report_path, 'w') as report_file:
        json.dump(smells, report_file, indent=4)
    print(f"Code smells detected and saved to {report_path}")

# Example usage
if __name__ == "__main__":
    directory_path = "path/to/your/python/code"  # Replace with your Python directory path
    report_path = "code_smells_report.json"  # Replace with your desired output path
    detect_code_smells_in_directory(directory_path, report_path)