import re

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    # Adicione 'float' e 'char' como tipos suportados
    KEYWORDS = ['int', 'float', 'char', 'def', 'print']
    OPERATORS = ['=', '+', '-'] # Adicione outros operadores se necessário
    DELIMITERS = ['{', '}', '(', ')', ';', ',']

    TOKEN_SPECIFICATIONS = [
        ('COMMENT', r'//.*'),
        ('WHITESPACE', r'\s+'),
        # Float deve vir antes de INTEGER para evitar conflito
        ('FLOAT', r'\d+\.\d+'),
        ('CHAR', r"'[^'\\]'"),
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('INTEGER', r'\d+'),
        ('OPERATOR', r'[=+\-*/]'),
        ('DELIMITER', r'[{}(),;]'),
    ]

    def __init__(self, text):
        self.text = text
        self.position = 0
        self.tokens = []
        self._tokenize()

    def _tokenize(self):
        token_patterns = [(name, re.compile(pattern)) for name, pattern in self.TOKEN_SPECIFICATIONS]

        while self.position < len(self.text):
            match = None
            for token_type, pattern in token_patterns:
                m = pattern.match(self.text, self.position)
                if m:
                    value = m.group(0)
                    if token_type == 'WHITESPACE' or token_type == 'COMMENT':
                        pass # Ignorar espaços em branco e comentários
                    elif token_type == 'IDENTIFIER':
                        if value in self.KEYWORDS:
                            self.tokens.append(Token(value.upper(), value)) # Ex: INT, FLOAT, CHAR, DEF
                        else:
                            self.tokens.append(Token('ID', value))
                    elif token_type == 'INTEGER':
                        self.tokens.append(Token('INT_LITERAL', int(value)))
                    elif token_type == 'FLOAT':
                        self.tokens.append(Token('FLOAT_LITERAL', float(value)))
                    elif token_type == 'CHAR':
                        self.tokens.append(Token('CHAR_LITERAL', value[1])) # Pega o caractere entre aspas
                    elif token_type == 'OPERATOR':
                        self.tokens.append(Token(value, value)) # Ex: =, +
                    elif token_type == 'DELIMITER':
                        self.tokens.append(Token(value, value)) # Ex: {, }
                    else:
                        raise Exception(f"Unknown token type: {token_type}")
                    self.position = m.end(0)
                    match = True
                    break
            if not match:
                raise Exception(f"Lexer error: Unexpected character at position {self.position}: '{self.text[self.position]}'")
        self.tokens.append(Token('EOF', None)) # End of File token

    def get_tokens(self):
        return self.tokens

# Exemplo de uso (para testar o lexer)
if __name__ == '__main__':
    code = """
    int x; // Global variable
    def myFunc(a, b) {
        int y;
        y = a + b;
        print(y);
    }
    main() {
        x = 10;
        myFunc(1, 2);
        // This is a comment
    }
    """
    lexer = Lexer(code)
    for token in lexer.get_tokens():
        print(token)