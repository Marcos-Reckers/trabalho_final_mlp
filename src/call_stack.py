"""
Este módulo implementa as estruturas de dados para gerenciamento da pilha de 
chamadas do interpretador. Define a classe ActivationRecord que representa um 
registro de ativação para cada chamada de função, armazenando variáveis locais, 
referências para frames pai (escopo dinâmico) e frames léxicos (escopo estático). 
A classe CallStack gerencia a pilha destes registros, permitindo operações de 
push, pop e peek para controlar o fluxo de execução das funções.
"""


class ActivationRecord:
    def __init__(self, name, scope_type, parent_frame=None, lex_parent_frame=None):
        self.name = name
        self.scope_type = scope_type
        self.locals = {}
        self.parent_frame = parent_frame
        self.lex_parent_frame = lex_parent_frame

    def get_local(self, name):
        return self.locals.get(name)

    def set_local(self, name, value):
        self.locals[name] = value

    def __repr__(self):
        return f"AR(name='{self.name}', locals={self.locals}, type='{self.scope_type}')"


class CallStack:
    def __init__(self):
        self.stack = []

    def push(self, frame):
        self.stack.append(frame)

    def pop(self):
        if self.stack:
            return self.stack.pop()
        return None

    def peek(self):
        if self.stack:
            return self.stack[-1]
        return None

    def __repr__(self):
        return "\n".join(str(ar) for ar in reversed(self.stack))
