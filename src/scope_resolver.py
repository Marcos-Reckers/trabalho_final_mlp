from ast_nodes import *
from symbol_table import SymbolTable

class StaticScopeResolver:
    def __init__(self):
        self.current_scope = None # Top of the symbol table stack

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        for attr in dir(node):
            if not attr.startswith('_') and attr != 'scope_info':
                value = getattr(node, attr)
                if isinstance(value, list):
                    for item in value:
                        self.visit(item)
                elif isinstance(value, ASTNode):
                    self.visit(value)

    def visit_ProgramNode(self, node):
        self.current_scope = SymbolTable(name="global")
        for decl in node.declarations:
            self.visit(decl)

    def visit_VarDeclNode(self, node):
        # For variable declarations, store reference to this node (or just its name/type)
        # For simplicity, let's just store the name, and the interpreter will resolve its value
        self.current_scope.insert(node.var_name, {'type': node.var_type, 'node': node})

    def visit_FunctionDefNode(self, node):
        # Store function definition in the current (enclosing) scope
        self.current_scope.insert(node.name, {'type': 'function', 'node': node, 'closure_scope': self.current_scope})

        # Enter new scope for the function body
        previous_scope = self.current_scope
        self.current_scope = SymbolTable(parent=previous_scope, name=f"func_{node.name}_scope")

        # Process parameters
        for param in node.params:
            self.current_scope.insert(param.var_name, {'type': 'param', 'node': param})

        self.visit(node.body) # Visit the function body
        self.current_scope = previous_scope # Exit function scope

    def visit_BlockNode(self, node):
        # For block scopes, create a new symbol table
        # Only if it's not a function block, or we explicitly want nested block scopes
        # For simplicity, let's treat blocks as simple containers unless they're function bodies
        # If you need full block scoping, you'd push/pop here.
        # For now, let's just visit statements within the block
        for stmt in node.statements:
            self.visit(stmt)

    def visit_IdentifierNode(self, node):
        # This is where the magic happens for static scoping:
        # Resolve the identifier to its declaration in the symbol table hierarchy
        # and store a reference.
        # This 'lookup' happens at "compile time" (analysis time).
        symbol_info = self.current_scope.lookup(node.name)
        if not symbol_info:
            raise Exception(f"Static Scope Error: Identifier '{node.name}' not defined.")
        node.scope_info = symbol_info # Store the resolved symbol info in the AST node
        # For a more robust solution, scope_info might be a pointer to the actual symbol table entry

    def visit_AssignNode(self, node):
        self.visit(node.identifier)
        self.visit(node.expression)

    def visit_CallNode(self, node):
        self.visit(node.function_name)
        for arg in node.args:
            self.visit(arg)

    def visit_PrintNode(self, node):
        self.visit(node.expression)

    def visit_IntegerNode(self, node):
        pass # Nothing to resolve for literals

# Example of use (to test the static scope resolver)
if __name__ == '__main__':
    from lexer import Lexer
    from parser import Parser
    code = """
    int x; // Global
    def f() {
      // 'x' here refers to the global 'x' in static scope
      print(x);
    }
    def g() {
      int x; // Local to g
      x = 2;
      f();
    }
    main() {
      x = 1;
      g();
    }
    """
    lexer = Lexer(code)
    parser = Parser(lexer.get_tokens())
    ast = parser.parse_program()

    resolver = StaticScopeResolver()
    resolver.visit(ast)

    # You would typically inspect the AST to see the `scope_info`
    # For a simple print, you might need a helper:
    def print_resolved_ast(node, indent=0):
        if isinstance(node, IdentifierNode) and node.scope_info:
            print("  " * indent + f"ID({node.name}) -> Resolved to: {node.scope_info['node'].__class__.__name__}")
        elif isinstance(node, ASTNode):
            print("  " * indent + f"{node.__class__.__name__}")
            for attr, value in node.__dict__.items():
                if attr not in ['scope_info'] and not attr.startswith('_'):
                    if isinstance(value, list):
                        print("  " * (indent + 1) + f"{attr}: [")
                        for item in value:
                            print_resolved_ast(item, indent + 2)
                        print("  " * (indent + 1) + "]")
                    else:
                        print("  " * (indent + 1) + f"{attr}:")
                        print_resolved_ast(value, indent + 2)
        else:
            print("  " * indent + str(node))

    # print_resolved_ast(ast) # Uncomment to see the resolved AST
    print("Static scope resolution complete. AST nodes should now have scope_info for identifiers.")