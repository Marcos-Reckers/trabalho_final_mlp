"""
Este módulo implementa o verificador semântico que analisa a AST para detectar 
erros semânticos antes da interpretação. Verifica se variáveis foram declaradas 
antes do uso, se os tipos são compatíveis em atribuições e operações, se funções 
são chamadas com o número correto de argumentos e tipos compatíveis. Mantém uma 
tabela de símbolos para rastrear declarações e tipos, e aplica regras de coerção 
de tipos (como conversão implícita de int para float).
"""

from ast_nodes import ASTNode, VarDeclNode, FunctionDefNode, CallNode, PrintNode, BlockNode
from symbol_table import SymbolTable


class SemanticChecker:
    def __init__(self):
        self.symbol_table = SymbolTable()

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        if hasattr(node, '__dict__'):
            for child in node.__dict__.values():
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, ASTNode):
                            self.visit(item)
                elif isinstance(child, ASTNode):
                    self.visit(child)

    def visit_ProgramNode(self, node):
        for declaration in node.declarations:
            if isinstance(declaration, VarDeclNode):
                self.symbol_table.insert(declaration.var_name, {
                                         'type': declaration.var_type})
            elif isinstance(declaration, FunctionDefNode):
                self.symbol_table.insert(
                    declaration.name, {'type': 'function', 'node': declaration})

        for declaration in node.declarations:
            if isinstance(declaration, FunctionDefNode):
                self.visit(declaration)

    def visit_FunctionDefNode(self, node):
        parent_scope = self.symbol_table
        self.symbol_table = SymbolTable(parent=parent_scope)

        if hasattr(node, 'params'):
            for param in node.params:
                self.symbol_table.insert(
                    param.var_name, {'type': param.var_type})

        self.visit(node.body)

        self.symbol_table = parent_scope

    def visit_BlockNode(self, node):
        for statement in node.statements:
            if isinstance(statement, VarDeclNode):
                self.symbol_table.insert(statement.var_name, {
                                         'type': statement.var_type})

        for statement in node.statements:
            if not isinstance(statement, VarDeclNode):
                self.visit(statement)

    def visit_VarDeclNode(self, node):
        pass

    def visit_AssignNode(self, node):
        var_name = node.identifier.name
        var_info = self.symbol_table.lookup(var_name)
        if not var_info:
            raise Exception(
                f"Semantic Error: Variable '{var_name}' not declared.")

        expr_type = self.visit(node.expression)
        var_type = var_info['type']

        if var_type != expr_type:
            if var_type == 'float' and expr_type == 'int':
                pass
            else:
                raise Exception(
                    f"Semantic Error: Cannot assign type '{expr_type}' to variable '{var_name}' of type '{var_type}'.")

    def visit_IdentifierNode(self, node):
        var_info = self.symbol_table.lookup(node.name)
        if not var_info:
            raise Exception(
                f"Semantic Error: Variable '{node.name}' not declared.")
        return var_info['type']

    def visit_IntegerNode(self, node):
        return 'int'

    def visit_FloatNode(self, node):
        return 'float'

    def visit_CharNode(self, node):
        return 'char'

    def visit_BinaryOpNode(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        if left_type == 'float' or right_type == 'float':
            return 'float'
        return 'int'

    def visit_CallNode(self, node):
        func_name = node.function_name.name
        func_info = self.symbol_table.lookup(func_name)
        if func_name == 'print':
            for arg in node.args:
                self.visit(arg)
            return None
        if not func_info or func_info['type'] != 'function':
            raise Exception(
                f"Semantic Error: Function '{func_name}' not declared.")
        func_node = func_info['node']
        if len(node.args) != len(func_node.params):
            raise Exception(
                f"Semantic Error: Function '{func_name}' expects {len(func_node.params)} arguments, got {len(node.args)}.")
        for arg_node, param in zip(node.args, func_node.params):
            arg_type = self.visit(arg_node)
            if arg_type != param.var_type and not (param.var_type == 'float' and arg_type == 'int'):
                raise Exception(
                    f"Semantic Error: Cannot pass type '{arg_type}' to parameter '{param.var_name}' of type '{param.var_type}' in call to '{func_name}'.")
        return None
