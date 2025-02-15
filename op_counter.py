import ast 
class Counter(ast.NodeVisitor):
        def __init__(self):
            self.operators = 0
            self.operands = 0

        def visit_BinOp(self, node):
            self.operators += 1 
            self.operands += 2 
            self.generic_visit(node)

        def visit_UnaryOp(self, node):
            self.operators += 1  
            self.operands += 1  
            self.generic_visit(node)

        def visit_AugAssign(self, node):
            self.operators += 1
            self.operands += 1 
            self.generic_visit(node)

        def visit_Assign(self, node):
            self.operators += 1 
            self.operands += len(node.targets) + 1 
            self.generic_visit(node)


        def visit_Compare(self, node):
            self.operators += len(node.ops)  
            self.operands += len(node.comparators) + 1
            self.generic_visit(node)

        def visit_BoolOp(self, node):
            self.operators += len(node.values) - 1  
            self.operands += len(node.values)  
            self.generic_visit(node)