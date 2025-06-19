from lexer import Token
from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index]

    def _advance(self):
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = Token('EOF', None)

    def _eat(self, token_type):
        if self.current_token.type == token_type:
            value = self.current_token.value
            self._advance()
            return value
        else:
            raise Exception(f"Parser error: Expected {token_type}, got {self.current_token.type}")

    def parse_program(self):
        declarations = []
        while self.current_token.type != 'EOF':
            if self.current_token.type in ['INT', 'FLOAT', 'CHAR']:
                declarations.append(self._parse_var_declaration())
            elif self.current_token.type == 'DEF':
                declarations.append(self._parse_function_definition())
            elif self.current_token.type == 'ID' and self.current_token.value == 'main':
                declarations.append(self._parse_main_function())
            else:
                raise Exception(f"Parser error: Unexpected token at program level: {self.current_token.type}")
        return ProgramNode(declarations)

    def _parse_var_declaration(self):
        var_type = self.current_token.value
        self._eat(self.current_token.type) # INT, FLOAT, CHAR
        var_name = self._eat('ID')
        self._eat(';')
        return VarDeclNode(var_type, var_name)

    def _parse_function_definition(self):
        self._eat('DEF')
        func_name = self._eat('ID')
        self._eat('(')
        params = []
        if self.current_token.type in ['INT', 'FLOAT', 'CHAR']:
            while True:
                param_type = self.current_token.value
                self._eat(self.current_token.type)
                param_name = self._eat('ID')
                params.append(VarDeclNode(param_type, param_name))
                if self.current_token.type == ',':
                    self._eat(',')
                else:
                    break
        self._eat(')')
        body = self._parse_block()
        return FunctionDefNode(func_name, params, body)

    def _parse_main_function(self):
        self._eat('ID') # 'main'
        self._eat('(')
        self._eat(')')
        body = self._parse_block()
        return FunctionDefNode('main', [], body)

    def _parse_block(self):
        self._eat('{')
        statements = []
        while self.current_token.type != '}':
            statements.append(self._parse_statement())
        self._eat('}')
        return BlockNode(statements)

    def _parse_statement(self):
        if self.current_token.type == 'ID':
            if self.tokens[self.current_token_index + 1].type == '=':
                return self._parse_assignment_statement()
            elif self.tokens[self.current_token_index + 1].type == '(': 
                return self._parse_call_statement()
            else:
                raise Exception(f"Parser error: Unexpected ID usage in statement: {self.current_token.type}")
        elif self.current_token.type in ['INT', 'FLOAT', 'CHAR']:
            return self._parse_var_declaration() # Local declaration
        elif self.current_token.type == 'PRINT':
            return self._parse_print_statement()
        else:
            raise Exception(f"Parser error: Unexpected token in statement: {self.current_token.type}")

    def _parse_assignment_statement(self):
        identifier = IdentifierNode(self._eat('ID'))
        self._eat('=')
        expression = self._parse_expression()
        self._eat(';')
        return AssignNode(identifier, expression)

    def _parse_call_statement(self):
        func_name = IdentifierNode(self._eat('ID'))
        self._eat('(')
        args = []
        if self.current_token.type != ')':
            args.append(self._parse_expression())
            while self.current_token.type == ',':
                self._eat(',')
                args.append(self._parse_expression())
        self._eat(')')
        self._eat(';')
        return CallNode(func_name, args)

    def _parse_print_statement(self):
        self._eat('PRINT')
        self._eat('(')
        expr = self._parse_expression()
        self._eat(')')
        self._eat(';')
        return PrintNode(expr)

    def _parse_expression(self):
        node = self._parse_term()
        while self.current_token.type in ['+', '-']:
            op = self._eat(self.current_token.type)
            right = self._parse_term()
            node = BinaryOpNode(node, op, right)
        return node

    def _parse_term(self):
        # Suporte para int, float, char literals e identificadores
        if self.current_token.type == 'INT_LITERAL':
            value = self._eat('INT_LITERAL')
            return IntegerNode(value)
        elif self.current_token.type == 'FLOAT_LITERAL':
            value = self._eat('FLOAT_LITERAL')
            return FloatNode(value)
        elif self.current_token.type == 'CHAR_LITERAL':
            value = self._eat('CHAR_LITERAL')
            return CharNode(value)
        elif self.current_token.type == 'ID':
            name = self._eat('ID')
            return IdentifierNode(name)
        else:
            raise Exception(f"Parser error: Expected expression, got {self.current_token.type}")

# Exemplo de uso (para testar o parser)
if __name__ == '__main__':
    from lexer import Lexer
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

    # Simple AST traversal to verify
    def print_ast(node, indent=0):
        if isinstance(node, ASTNode):
            print("  " * indent + f"{node.__class__.__name__}")
            for attr, value in node.__dict__.items():
                if attr not in ['scope_info'] and not attr.startswith('_'): # Avoid internal attrs
                    if isinstance(value, list):
                        print("  " * (indent + 1) + f"{attr}: [")
                        for item in value:
                            print_ast(item, indent + 2)
                        print("  " * (indent + 1) + "]")
                    else:
                        print("  " * (indent + 1) + f"{attr}:")
                        print_ast(value, indent + 2)
        else:
            print("  " * indent + str(node))

    print_ast(ast)