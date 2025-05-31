class ActivationRecord:
    def __init__(self, name, scope_type, parent_frame=None, lex_parent_frame=None):
        self.name = name # Nome da função
        self.scope_type = scope_type # 'static' ou 'dynamic'
        self.locals = {} # Variáveis locais para este frame
        self.parent_frame = parent_frame # Para escopo dinâmico (quem chamou)
        self.lex_parent_frame = lex_parent_frame # Para escopo estático (ambiente léxico)

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
        return "\n".join(str(ar) for ar in reversed(self.stack)) # Top of stack is last element