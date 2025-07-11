"""
Este módulo implementa o resolvedor de escopo estático que percorre a AST e 
resolve referências de identificadores de acordo com as regras de escopo léxico. 
Constrói tabelas de símbolos aninhadas representando a estrutura de escopos do 
programa e associa cada uso de identificador à sua declaração correspondente. 
Utiliza o padrão Visitor para percorrer os nós da AST e armazena informações 
de resolução nos próprios nós para uso posterior pelo interpretador.
"""

from ast_nodes import *
from symbol_table import SymbolTable


class StaticScopeResolver:
    def __init__(self):
        self.current_scope = None

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
        self.current_scope.insert(
            node.var_name, {'type': node.var_type, 'node': node})

    def visit_FunctionDefNode(self, node):
        self.current_scope.insert(
            node.name, {'type': 'function', 'node': node, 'closure_scope': self.current_scope})

        previous_scope = self.current_scope
        self.current_scope = SymbolTable(
            parent=previous_scope, name=f"func_{node.name}_scope")

        for param in node.params:
            self.current_scope.insert(
                param.var_name, {'type': 'param', 'node': param})

        self.visit(node.body)
        self.current_scope = previous_scope

    def visit_BlockNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_IdentifierNode(self, node):
        symbol_info = self.current_scope.lookup(node.name)
        if not symbol_info:
            raise Exception(
                f"Static Scope Error: Identifier '{node.name}' not defined.")
        node.scope_info = symbol_info
        if 'type' in symbol_info:
            node.var_type = symbol_info['type']

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
        pass


if __name__ == '__main__':
    from lexer import Lexer
    from parser import Parser
    code = """
    int x;
    def f() {
      print(x);
    }
    def g() {
      int x;
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

    def print_resolved_ast(node, indent=0):
        if isinstance(node, IdentifierNode) and node.scope_info:
            print("  " * indent +
                  f"ID({node.name}) -> Resolved to: {node.scope_info['node'].__class__.__name__}")
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

    print("Static scope resolution complete. AST nodes should now have scope_info for identifiers.")
