"""
Este módulo contém as definições de todos os nós da Árvore Sintática Abstrata (AST) 
do interpretador. Define classes para representar diferentes construções da linguagem 
como declarações de variáveis, definições de funções, blocos de código, atribuições, 
chamadas de função, identificadores, literais numéricos e de caracteres, comandos de 
impressão e operações binárias. Cada nó herda de ASTNode e armazena informações 
específicas sobre sua estrutura sintática.
"""


class ASTNode:
    pass


class ProgramNode(ASTNode):
    def __init__(self, declarations):
        self.declarations = declarations


class VarDeclNode(ASTNode):
    def __init__(self, var_type, var_name):
        self.var_type = var_type
        self.var_name = var_name


class FunctionDefNode(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class BlockNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements


class AssignNode(ASTNode):
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression


class CallNode(ASTNode):
    def __init__(self, function_name, args):
        self.function_name = function_name
        self.args = args


class IdentifierNode(ASTNode):
    def __init__(self, name, var_type=None):
        self.name = name
        self.var_type = var_type
        self.scope_info = None


class IntegerNode(ASTNode):
    def __init__(self, value):
        self.value = value


class PrintNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression


class FloatNode(ASTNode):
    def __init__(self, value):
        self.value = value


class CharNode(ASTNode):
    def __init__(self, value):
        self.value = value


class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
