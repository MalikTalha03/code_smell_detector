
from calculate import *

THRESHOLDS = {
    "PAR_LPL": 5,    # Long Parameter List (LPL)
    "MLOC_LM": 38,  # Method/Function Lines of Code (LM)
    "DOC_LSC": 3,    # Depth of Closure (LSC)
    "CLOC_LC": 29,  # Class Lines of Code (LC)
    "NBC_LBCL": 3,    # Number of Base Classes 
    "NOC_LLF": 48,   # Number of Characters
    "PAR_LLF": 3,   # Number of Parameters for LLF
    "NOO_LLF": 7,    # Number of Operators and Operands (LLF)
    "NOC_LTCE": 54,  # Number of Characters for LTCE
    "NOL_LTCE": 3,    # Number of Lines (LTCE)
    "NOC_CCC": 62,    # Number of Comprehensions in CCC
    "NOFF_CCC": 3,   # Number of For Clauses and Filters in CCC
    "NOO_CCC": 8,    # Number of Operators/Operands in CCC
}

def add_smell(smells, name, lineno, details, file_path):
    """Add a code smell to the list."""
    smells.append({
        "file": file_path,
        "code_smell": name,
        "line_number": lineno,
        "details": details
    })

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

def detect_lc(node, smells, file_path,source_code):
    """Detect Large Class (LC)."""
    s_code = source_code
    cloc = calculate_cloc(node, s_code)
    if cloc > THRESHOLDS["CLOC_LC"]:
        add_smell(smells, "Large Class (LC)", node.lineno, f"Class Lines of Code: {cloc}", file_path)
        
def detect_lsc(node, smells, file_path):
    """Detect Long Scope Chaining (LSC)."""
    doc = calculate_doc(node)
    if doc > THRESHOLDS["DOC_LSC"]:
        add_smell(smells, "Long Scope Chaining (LSC)", node.lineno, f"Nested Levels: {doc}", file_path)

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

