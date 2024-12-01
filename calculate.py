import ast
# Metric calculation functions
def calculate_par(node):
    """Calculate Number of Parameters (PAR)."""
    return len(node.args.args)


def calculate_doc(node):
    """Calculate Depth of Closure (DOC)."""
    return count_nested_levels(node)

def count_nested_levels(node):
    """Count nested levels for Long Scope Chaining (LSC)."""
    max_depth = 1
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.With)):
            max_depth = max(max_depth, 1 + count_nested_levels(child))
    return max_depth

def calculate_mloc(node, source_code):
    """Calculate Method/Function Lines of Code (MLOC), ignoring empty lines."""
    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
        source_code = source_code.split("\n")
        function_lines = source_code[node.lineno - 1:node.end_lineno] 
        function_lines = [line for line in function_lines if not line.strip().startswith("#") and not line.strip().startswith("'''") and not line.strip().startswith('"""')]
        mloc = sum(1 for line in function_lines if line.strip()) 
            
    else:
        mloc = len(node.body)
    return mloc


def calculate_cloc(node, source_code):
    """Calculate Class Lines of Code (CLOC), ignoring empty lines."""
    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
        source_code = source_code.split("\n")
        class_lines = source_code[node.lineno - 1:node.end_lineno] 
        class_lines = [line for line in class_lines if not line.strip().startswith("#") and not line.strip().startswith("'''") and not line.strip().startswith('"""')]
        # Count non-empty lines (ignoring lines with only whitespace)
        cloc = sum(1 for line in class_lines if line.strip())  # Count only non-empty lines
    else:
        # Fallback for older Python versions without `end_lineno`
        cloc = len(node.body)
    return cloc

def calculate_nbc(node):
    """Calculate Number of Base Classes (NBC)."""
    return len(node.bases)

def calculate_noc(node,s_code):
    """Calculate Number of Characters (NOC)."""
    node_source_code = s_code[node.lineno - 1:node.end_lineno]
    length = sum(len(line.strip()) for line in node_source_code)
    return length

def calculate_noo(node):
    """Calculate Number of Operators and Operands (NOO)."""
    return count_operators_and_operands(node)

def calculate_noo(node):
    """Calculate Number of Operators and Operands (NOO)."""
    return count_operators_and_operands(node)

def count_operators_and_operands(node):
    class Counter(ast.NodeVisitor):
        def __init__(self):
            self.operators = 0
            self.operands = 0

        # Arithmetic Operators (+, -, *, /, //, %, **)
        def visit_BinOp(self, node):
            self.operators += 1  # Count the operator
            self.operands += 2  # Left and right are operands
            self.generic_visit(node)

        # Unary Operators (-x, ~x)
        def visit_UnaryOp(self, node):
            self.operators += 1  # Unary operator
            self.operands += 1  # Operand (e.g., `-x`)
            self.generic_visit(node)

        # Assignment Operators (=, +=, -=, etc.)
        def visit_AugAssign(self, node):
            self.operators += 1  # Assignment operator
            self.operands += 1  # Target variable
            self.generic_visit(node)

        def visit_Assign(self, node):
            self.operators += 1  # Simple assignment `=`
            self.operands += len(node.targets) + 1  # All targets + value
            self.generic_visit(node)

        # Comparison Operators (==, !=, <, >, <=, >=)
        def visit_Compare(self, node):
            self.operators += len(node.ops)  # Count comparison operators
            self.operands += len(node.comparators) + 1  # Comparators + left operand
            self.generic_visit(node)

        # Logical Operators (and, or, not)
        def visit_BoolOp(self, node):
            self.operators += len(node.values) - 1  # Logical operator count
            self.operands += len(node.values)  # Each value is an operand
            self.generic_visit(node)
        
    counter = Counter()
    counter.visit(node)
    return counter.operators + counter.operands


def calculate_nol(node):
    """Calculate Number of Lines (NOL)."""
    return len(ast.dump(node).splitlines())

def calculate_noff(node):
    """Calculate Number of For Clauses and Filters (NOFF)."""
    noff = 0
    if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        for generator in node.generators:  # `generators` contains `ast.comprehension` nodes
            noff += 1  # Count the `for` clause
            noff += len(generator.ifs)  # Add the number of filters for this clause
    return noff
