"""
Este módulo implementa a estrutura de dados da tabela de símbolos para gerenciar 
escopos e símbolos no interpretador. A classe SymbolTable mantém um mapeamento 
entre nomes de identificadores e suas informações associadas (tipo, valor, etc.), 
com suporte para escopos aninhados através de referências para tabelas pai. 
Fornece métodos para inserção de símbolos, busca em escopo atual e busca 
hierárquica percorrendo a cadeia de escopos pais.
"""


class SymbolTable:
    def __init__(self, parent=None, name="global"):
        self.symbols = {}
        self.parent = parent
        self.name = name

    def insert(self, name, symbol_info):
        if name in self.symbols:
            raise Exception(
                f"Redeclaration error: Symbol '{name}' already exists in current scope.")
        self.symbols[name] = symbol_info

    def lookup(self, name):
        current_scope = self
        while current_scope:
            if name in current_scope.symbols:
                return current_scope.symbols[name]
            current_scope = current_scope.parent
        return None

    def lookup_current_scope(self, name):
        return self.symbols.get(name)

    def __repr__(self):
        symbols_str = ", ".join([f"{k}: {v}" for k, v in self.symbols.items()])
        parent_name = self.parent.name if self.parent else "None"
        return f"SymbolTable(name='{self.name}', parent='{parent_name}', symbols={{{symbols_str}}})"


if __name__ == '__main__':
    global_scope = SymbolTable(name="global")
    global_scope.insert('x', {'type': 'int', 'value': 10})
    global_scope.insert('y', {'type': 'float', 'value': 3.14})
    global_scope.insert('c', {'type': 'char', 'value': 'a'})

    func_f_scope = SymbolTable(parent=global_scope, name="f")
    func_f_scope.insert('y', {'type': 'int', 'value': 20})

    func_g_scope = SymbolTable(parent=global_scope, name="g")
    func_g_scope.insert('x', {'type': 'float', 'value': 30.5})

    print("Global x:", global_scope.lookup('x'))
    print("Global y:", global_scope.lookup('y'))
    print("Global c:", global_scope.lookup('c'))
    print("f's y:", func_f_scope.lookup('y'))
    print("f's x (looks up parent):", func_f_scope.lookup('x'))
    print("g's x (local):", func_g_scope.lookup('x'))
    print("g's y (not found, looks up parent):", func_g_scope.lookup('y'))
