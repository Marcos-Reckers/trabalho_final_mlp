from ast_nodes import *
from call_stack import CallStack, ActivationRecord
from symbol_table import SymbolTable

class Interpreter:
    def __init__(self, ast, scope_mode):
        self.ast = ast
        self.scope_mode = scope_mode # 'static' or 'dynamic'
        self.call_stack = CallStack()
        self.global_scope = SymbolTable(name="global") # Stores global variables and function definitions

        # Pre-process functions and global variables for both scopes
        self._setup_global_scope()

    def _setup_global_scope(self):
        for declaration in self.ast.declarations:
            if isinstance(declaration, VarDeclNode):
                # Ensure 'value' key is always present for variables
                self.global_scope.insert(declaration.var_name, {'type': declaration.var_type, 'value': None})
            elif isinstance(declaration, FunctionDefNode):
                # For functions, store the function definition node itself
                # In static scope, also store the lexical environment where it was defined
                self.global_scope.insert(declaration.name, {
                    'type': 'function',
                    'node': declaration,
                    'closure_scope': self.global_scope if self.scope_mode == 'static' else None # Closure for static
                })
        # Add 'print' as a built-in function (it doesn't have a 'value' either)
        self.global_scope.insert('print', {'type': 'builtin_function', 'node': None})


    def interpret(self):
        # Start execution by finding and calling the 'main' function
        main_func_info = self.global_scope.lookup('main')
        if not main_func_info or main_func_info['type'] != 'function':
            raise Exception("No 'main' function found in the program.")

        main_func_node = main_func_info['node']

        # Push the initial 'main' activation record
        main_frame = ActivationRecord(
            name='main',
            scope_type=self.scope_mode,
            parent_frame=None,
            # For 'main' in static scope, its lexical parent is the global scope
            lex_parent_frame=self.global_scope if self.scope_mode == 'static' else None
        )
        self.call_stack.push(main_frame)

        self._print_call_stack_state("Program Start")

        self.visit(main_func_node.body) # Start execution of main's body

        self.call_stack.pop() # Pop main frame

        self._print_call_stack_state("Program End")


    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit method for {type(node).__name__}")

    def visit_ProgramNode(self, node):
        # This is handled in interpret() by calling main.
        pass

    def visit_BlockNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_VarDeclNode(self, node):
        # Local variable declaration. Initialize in the current AR.
        current_frame = self.call_stack.peek()
        if current_frame:
            current_frame.set_local(node.var_name, None) # Initialize with default value (e.g., None, 0)
        # Global variable declarations are handled in _setup_global_scope

    def visit_AssignNode(self, node):
        identifier_name = node.identifier.name
        value_to_assign = self.visit(node.expression) # Evaluate the right-hand side

        found_variable_location = False
        target_ar = None
        target_scope = None # To hold either an AR or the global_scope

        # Try to find the variable in the current frame or its ancestors based on scope mode
        current_frame = self.call_stack.peek()

        if self.scope_mode == 'static':
            # For static scope, we need to find the correct lexical parent.
            # This is still a simplified approach. A full implementation would involve:
            # 1. During StaticScopeResolver, store the 'depth' or a direct reference to the symbol table entry
            #    of the declared variable.
            # 2. At runtime, follow `lex_parent_frame` pointers on the CallStack until the correct scope is found.

            # Simplified static lookup for assignment:
            # First, check the current activation record (local variables/parameters)
            if current_frame and identifier_name in current_frame.locals:
                current_frame.set_local(identifier_name, value_to_assign)
                found_variable_location = True
            else:
                # Then, check the global scope. For a true static scope, you'd follow
                # the lexical parent chain.
                # In this simplified model, global is the only "outer" scope.
                global_var_info = self.global_scope.lookup_current_scope(identifier_name)
                if global_var_info and global_var_info['type'] != 'function':
                    global_var_info['value'] = value_to_assign
                    found_variable_location = True

        elif self.scope_mode == 'dynamic':
            # Dynamic scope: search up the call stack (parent_frame chain)
            temp_frame = current_frame
            while temp_frame:
                if identifier_name in temp_frame.locals:
                    temp_frame.set_local(identifier_name, value_to_assign)
                    found_variable_location = True
                    break
                temp_frame = temp_frame.parent_frame
            # If not found in any activation record on the stack, check global scope
            if not found_variable_location:
                global_var_info = self.global_scope.lookup_current_scope(identifier_name)
                if global_var_info and global_var_info['type'] != 'function':
                    global_var_info['value'] = value_to_assign
                    found_variable_location = True

        if not found_variable_location:
            raise Exception(f"Assignment error: Variable '{identifier_name}' not found or cannot be assigned.")

        self._print_call_stack_state(f"Assignment: {identifier_name} = {value_to_assign}")


    def visit_CallNode(self, node):
        func_name = node.function_name.name
        func_info = self.global_scope.lookup(func_name) # Functions are always looked up globally

        if not func_info:
            raise Exception(f"Call error: Function '{func_name}' not defined.")

        if func_info['type'] == 'builtin_function' and func_name == 'print':
            self._handle_print(node.args)
            return

        func_node = func_info['node']

        # Evaluate arguments in the *caller's* context
        evaluated_args = [self.visit(arg_node) for arg_node in node.args]

        # Create a new activation record for the function call
        current_frame = self.call_stack.peek()

        new_frame = ActivationRecord(
            name=func_name,
            scope_type=self.scope_mode,
            parent_frame=current_frame if self.scope_mode == 'dynamic' else None, # Caller is parent for dynamic
            # For static scope, the lexical parent is the scope where the function was DEFINED (its closure)
            lex_parent_frame=func_info['closure_scope'] if self.scope_mode == 'static' else None
        )

        # Pass parameters to the new frame's locals
        if len(func_node.params) != len(evaluated_args):
            raise Exception(f"Function call error: '{func_name}' expects {len(func_node.params)} arguments, but got {len(evaluated_args)}.")
        for i, param in enumerate(func_node.params):
            new_frame.set_local(param.var_name, evaluated_args[i])

        self.call_stack.push(new_frame)
        self._print_call_stack_state(f"Function Call: {func_name}")

        self.visit(func_node.body) # Execute function body

        self.call_stack.pop()
        self._print_call_stack_state(f"Function Return: {func_name}")


    def visit_IdentifierNode(self, node):
        identifier_name = node.name
        value = None

        if self.scope_mode == 'static':
            # Static scope: Search from the current AR's lexical parent chain (closure)
            # This is the correct way to handle static scope with nested functions.
            current_ar_or_scope = self.call_stack.peek() # Start from the current AR
            if not current_ar_or_scope: # If call stack is empty (e.g., in global scope before main)
                current_ar_or_scope = self.global_scope # Treat global as the base

            # Follow lexical parent chain
            temp_scope = current_ar_or_scope
            while temp_scope:
                # Check if it's an ActivationRecord (local variable/parameter)
                if isinstance(temp_scope, ActivationRecord) and identifier_name in temp_scope.locals:
                    value = temp_scope.get_local(identifier_name)
                    return value
                # Check if it's a SymbolTable (global variable or variables in lexical parent scopes)
                elif isinstance(temp_scope, SymbolTable):
                    symbol_info = temp_scope.lookup_current_scope(identifier_name)
                    if symbol_info and symbol_info['type'] != 'function': # Make sure it's a variable, not a function
                        value = symbol_info['value']
                        return value

                # Move up the lexical chain
                if isinstance(temp_scope, ActivationRecord):
                    temp_scope = temp_scope.lex_parent_frame # Move to lexical parent AR or SymbolTable
                elif isinstance(temp_scope, SymbolTable):
                    temp_scope = temp_scope.parent # Move to parent SymbolTable
                else:
                    break # Should not happen

            raise Exception(f"Static Scope Error: Undefined variable '{identifier_name}'.")


        elif self.scope_mode == 'dynamic':
            # Dynamic scope: search up the call stack (parent_frame chain)
            temp_frame = self.call_stack.peek()
            while temp_frame:
                if identifier_name in temp_frame.locals:
                    value = temp_frame.get_local(identifier_name)
                    return value
                temp_frame = temp_frame.parent_frame

            # If not found in any activation record on the stack, check global scope
            global_var_info = self.global_scope.lookup_current_scope(identifier_name)
            if global_var_info and global_var_info['type'] != 'function':
                value = global_var_info['value']
                return value
            else:
                raise Exception(f"Dynamic Scope Error: Undefined variable '{identifier_name}'.")

    def visit_IntegerNode(self, node):
        return node.value

    def visit_PrintNode(self, node):
        value = self.visit(node.expression)
        print(f"OUTPUT: {value}")
        self._print_call_stack_state(f"Print statement: {value}")


    def _handle_print(self, args):
        if not args:
            print("OUTPUT: (empty line)")
            return
        # Assuming print can take multiple args, separated by comma or just one
        # For simplicity, let's just print the first argument
        value_to_print = self.visit(args[0])
        print(f"OUTPUT: {value_to_print}")
        # Not showing call stack state for built-in print calls to avoid too much noise,
        # but you can add it if desired.
        # self._print_call_stack_state(f"Built-in Print: {value_to_print}")


    def _print_call_stack_state(self, action):
        print(f"\n--- {action} ---")
        print("Call Stack:")
        if not self.call_stack.stack:
            print("  (empty)")
        else:
            # Print from bottom to top (oldest to newest call)
            for i, ar in enumerate(self.call_stack.stack):
                # Ensure handling of None for parent frames
                lex_parent_name = ar.lex_parent_frame.name if ar.lex_parent_frame else "None"
                parent_name = ar.parent_frame.name if ar.parent_frame else "None"
                print(f"  [{i}] {ar.name} (type='{ar.scope_type}', lex_parent='{lex_parent_name}', parent='{parent_name}'): {ar.locals}")

        print("Global Scope:")
        # Filter out functions and only include symbols that have a 'value' key
        global_vars_display = {}
        for k, v in self.global_scope.symbols.items():
            if 'value' in v: # Only include if 'value' key exists
                global_vars_display[k] = v['value']
        print(f"  {global_vars_display}")
        print("--------------------")