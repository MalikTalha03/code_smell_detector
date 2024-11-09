import os
import ast
import json
from typing import List, Dict

# Define thresholds for code smells (LLF, LSC, LPL, LMC)
THRESHOLDS = {
    'LPL': 5,    # Long Parameter List threshold
    'LSC': 4,    # Long Scope Chaining threshold 
    'LLF': 73,   # Long Lambda Function threshold in characters
    'LMC': 4,    # Long Message Chain threshold
}

class CodeSmellDetector(ast.NodeVisitor):
    def __init__(self):
        self.smells = []

    def add_smell(self, name: str, lineno: int, details: str, file_path: str):
        """Add a code smell to the list."""
        self.smells.append({
            "file": file_path,
            "code_smell": name,
            "line_number": lineno,
            "details": details
        })

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Check for Long Parameter List (LPL), Long Scope Chaining (LSC), and Long Lambda Function (LLF)."""
        try:
            # Long Parameter List (LPL)
            if len(node.args.args) > THRESHOLDS['LPL']:
                self.add_smell("Long Parameter List (LPL)", node.lineno, f"Parameters: {len(node.args.args)}", self.current_file)

            # Long Scope Chaining (LSC)
            if any(isinstance(stmt, (ast.If, ast.While, ast.For)) and self.count_nested_levels(stmt) > THRESHOLDS['LSC'] for stmt in node.body):
                self.add_smell("Long Scope Chaining (LSC)", node.lineno, f"Nested Levels > {THRESHOLDS['LSC']}", self.current_file)

            # Check inside function body for lambda functions
            for expr in ast.walk(node):
                if isinstance(expr, ast.Lambda):
                    lambda_length = len(ast.dump(expr))
                    if lambda_length > THRESHOLDS['LLF']:
                        self.add_smell("Long Lambda Function (LLF)", expr.lineno, f"Length: {lambda_length}", self.current_file)

        except Exception as e:
            print(f"Error in function definition analysis: {e}")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        """Check for Long Message Chain (LMC)."""
        try:
            chain_length = self.count_message_chain_length(node)
            if chain_length > THRESHOLDS['LMC']:
                self.add_smell("Long Message Chain (LMC)", node.lineno, f"Chain Length: {chain_length}", self.current_file)
        except Exception as e:
            print(f"Error in message chain analysis: {e}")
        self.generic_visit(node)

    def count_nested_levels(self, node) -> int:
        """Count nested levels for Long Scope Chaining (LSC)."""
        try:
            max_depth = 1
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.While, ast.For)):
                    max_depth = max(max_depth, 1 + self.count_nested_levels(child))
            return max_depth
        except Exception as e:
            print(f"Error counting nested levels: {e}")
            return 1  # Return a default depth in case of error

    def count_message_chain_length(self, node) -> int:
        """Count the length of the message chain for Long Message Chain (LMC)."""
        try:
            length = 0
            while isinstance(node, ast.Attribute):
                length += 1
                node = node.value
            return length
        except Exception as e:
            print(f"Error counting message chain length: {e}")
            return 0  # Return 0 in case of error

    def analyze_file(self, file_path: str) -> None:
        """Analyze a Python file for code smells."""
        self.current_file = file_path
        try:
            with open(file_path, 'r') as file:
                tree = ast.parse(file.read(), filename=file_path)
            self.visit(tree)
        except SyntaxError as e:
            print(f"Skipping file {file_path} due to syntax error: {e}")
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")

def detect_code_smells_in_directory(directory_path: str, report_path: str) -> None:
    """Scan a directory for Python files and detect code smells."""
    detector = CodeSmellDetector()

    # Traverse the directory for all .py files
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                detector.analyze_file(file_path)

    # Save the combined report to a JSON file in the main directory
    try:
        with open(report_path, 'w') as report_file:
            json.dump(detector.smells, report_file, indent=4)
        print(f"Code smells report saved to {report_path}")
    except Exception as e:
        print(f"Error saving report to {report_path}: {e}")
