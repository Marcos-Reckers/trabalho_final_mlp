class SymbolTable:
    def __init__(self, parent=None, name="global"):
        self.symbols = {}
        self.parent = parent
        self.name = name # For debugging/visualization

    def insert(self, name, symbol_info):
        if name in self.symbols:
            raise Exception(f"Redeclaration error: Symbol '{name}' already exists in current scope.")
        self.symbols[name] = symbol_info

    def lookup(self, name):
        """Looks up a symbol in the current scope and its parents."""
        current_scope = self
        while current_scope:
            if name in current_scope.symbols:
                return current_scope.symbols[name]
            current_scope = current_scope.parent
        return None # Not found

    def lookup_current_scope(self, name):
        """Looks up a symbol only in the current scope."""
        return self.symbols.get(name)

    def __repr__(self):
        symbols_str = ", ".join([f"{k}: {v}" for k, v in self.symbols.items()])
        parent_name = self.parent.name if self.parent else "None"
        return f"SymbolTable(name='{self.name}', parent='{parent_name}', symbols={{{symbols_str}}})"

# Exemplo de uso (para testar a tabela de símbolos)
if __name__ == '__main__':
    global_scope = SymbolTable(name="global")
    global_scope.insert('x', {'type': 'int', 'value': 10})

    func_f_scope = SymbolTable(parent=global_scope, name="f")
    func_f_scope.insert('y', {'type': 'int', 'value': 20})

    func_g_scope = SymbolTable(parent=global_scope, name="g")
    func_g_scope.insert('x', {'type': 'int', 'value': 30}) # Local 'x' in g

    print("Global x:", global_scope.lookup('x'))
    print("f's y:", func_f_scope.lookup('y'))
    print("f's x (looks up parent):", func_f_scope.lookup('x'))
    print("g's x (local):", func_g_scope.lookup('x'))
    print("g's y (not found, looks up parent):", func_g_scope.lookup('y')) # Should be None