class ASTNode:
    pass

class ProgramNode(ASTNode):
    def __init__(self, declarations):
        self.declarations = declarations # Lista de VarDeclNode e FunctionDefNode

class VarDeclNode(ASTNode):
    def __init__(self, var_type, var_name):
        self.var_type = var_type
        self.var_name = var_name

class FunctionDefNode(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params # Lista de VarDeclNode (apenas nome ou tipo e nome)
        self.body = body     # BlockNode

class BlockNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements # Lista de nós de statements

class AssignNode(ASTNode):
    def __init__(self, identifier, expression):
        self.identifier = identifier # IdentifierNode
        self.expression = expression

class CallNode(ASTNode):
    def __init__(self, function_name, args):
        self.function_name = function_name # IdentifierNode
        self.args = args # Lista de nós de expressão

class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name
        self.scope_info = None # Preenchido pelo StaticScopeResolver

class IntegerNode(ASTNode):
    def __init__(self, value):
        self.value = value

class PrintNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression