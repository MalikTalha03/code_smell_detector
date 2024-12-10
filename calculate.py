import ast
from op_counter import Counter

def calculate_par(node):
    """Calculate Number of Parameters (PAR)."""
    return len(node.args.args)

def calculate_doc(node):
    """Calculate Depth of Closure (DOC)."""
    return count_nested_levels(node)

def count_nested_levels(node):
    """Count nested levels for Long Scope Chaining (LSC)."""
    max_depth = 0
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.With)):
            max_depth = max(max_depth, 1 + count_nested_levels(child))
    return max_depth

def calculate_mloc(node, source_code):
    """Calculate Method Lines of Code (MLOC), ignoring decorators and empty lines."""
    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
        source_code = source_code.split("\n")
        function_lines = source_code[node.lineno - 1:node.end_lineno]
        function_lines = [
            line for line in function_lines
            if not line.strip().startswith("@")  # Exclude decorators
            and not line.strip().startswith("#")
            and not line.strip().startswith("'''")
            and not line.strip().startswith('"""')
        ]
        mloc = sum(1 for line in function_lines if line.strip())
    else:
        mloc = len(node.body)
    return mloc

def calculate_cloc(node, source_code):
    """Calculate Class Lines of Code (CLOC), ignoring empty lines."""
    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
        source_code = source_code.split("\n")
        class_lines = source_code[node.lineno - 1:node.end_lineno] 
        class_lines = [
            line for line in class_lines
            if not line.strip().startswith("#")
            and not line.strip().startswith("'''")
            and not line.strip().startswith('"""')
            and not line.strip().startswith("@") 
        ]
        cloc = sum(1 for line in class_lines if line.strip())  
    else:
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

def count_operators_and_operands(node):
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
        for generator in node.generators:  
            noff += 1 
            noff += len(generator.ifs) 
    return noff
