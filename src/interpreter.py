"""
Este módulo implementa o interpretador principal que executa a AST do programa. 
Suporta dois modos de escopo: estático (léxico) e dinâmico. Gerencia uma pilha 
de chamadas de funções, resolve referências de variáveis segundo as regras do 
modo de escopo escolhido, e executa operações como atribuições, chamadas de 
função e expressões aritméticas. Inclui visualização rica da pilha de execução 
e logging em JSON para análise posterior do comportamento do programa.
"""

from ast_nodes import *
from call_stack import CallStack, ActivationRecord
from symbol_table import SymbolTable
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.live import Live
from rich.align import Align
from time import sleep
import json


class Interpreter:
    def __init__(self, ast, scope_mode, json_log_file=None):
        self.ast = ast
        self.scope_mode = scope_mode
        self.call_stack = CallStack()
        self.global_scope = SymbolTable(name="global")
        self.json_log_file = json_log_file
        if json_log_file:
            with open(json_log_file, 'w') as f:
                f.write('')
        self._setup_global_scope()

    def _log_json_state(self, action, output=None):
        if not self.json_log_file:
            return
        stack = []
        for ar in self.call_stack.stack:
            stack.append({
                'name': ar.name,
                'scope_type': ar.scope_type,
                'parent': ar.parent_frame.name if ar.parent_frame else None,
                'lex_parent': ar.lex_parent_frame.name if ar.lex_parent_frame else None,
                'locals': ar.locals.copy()
            })
        global_vars = {}
        for k, v in self.global_scope.symbols.items():
            if 'value' in v:
                global_vars[k] = v['value']
        log_entry = {
            'action': action,
            'scope_mode': self.scope_mode,
            'call_stack': stack,
            'global_scope': global_vars
        }
        if output is not None:
            log_entry['output'] = output
        with open(self.json_log_file, 'a') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

    def _setup_global_scope(self):
        for declaration in self.ast.declarations:
            if isinstance(declaration, VarDeclNode):
                self.global_scope.insert(declaration.var_name, {
                                         'type': declaration.var_type, 'value': None})
            elif isinstance(declaration, FunctionDefNode):
                self.global_scope.insert(declaration.name, {
                    'type': 'function',
                    'node': declaration,
                    'closure_scope': self.global_scope if self.scope_mode == 'static' else None
                })
        self.global_scope.insert(
            'print', {'type': 'builtin_function', 'node': None})

    def interpret(self):
        main_func_info = self.global_scope.lookup('main')
        if not main_func_info or main_func_info['type'] != 'function':
            raise Exception("No 'main' function found in the program.")

        main_func_node = main_func_info['node']

        main_frame = ActivationRecord(
            name='main',
            scope_type=self.scope_mode,
            parent_frame=None,
            lex_parent_frame=self.global_scope if self.scope_mode == 'static' else None
        )
        self.call_stack.push(main_frame)

        self._print_call_stack_state("Program Start")

        self.visit(main_func_node.body)

        self.call_stack.pop()

        self._print_call_stack_state("Program End")

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit method for {type(node).__name__}")

    def visit_ProgramNode(self, node):
        pass

    def visit_BlockNode(self, node):
        for statement in node.statements:
            self.visit(statement)

    def visit_VarDeclNode(self, node):
        current_frame = self.call_stack.peek()
        if current_frame:
            if node.var_type == 'int':
                current_frame.set_local(node.var_name, 0)
            elif node.var_type == 'float':
                current_frame.set_local(node.var_name, 0.0)
            elif node.var_type == 'char':
                current_frame.set_local(node.var_name, '\0')
            else:
                current_frame.set_local(node.var_name, None)

    def visit_AssignNode(self, node):
        identifier_name = node.identifier.name
        value_to_assign = self.visit(node.expression)

        found_variable_location = False
        target_ar = None
        target_scope = None

        current_frame = self.call_stack.peek()

        if self.scope_mode == 'static':
            if current_frame and identifier_name in current_frame.locals:
                current_frame.set_local(identifier_name, value_to_assign)
                found_variable_location = True
            else:
                global_var_info = self.global_scope.lookup_current_scope(
                    identifier_name)
                if global_var_info and global_var_info['type'] != 'function':
                    global_var_info['value'] = value_to_assign
                    found_variable_location = True

        elif self.scope_mode == 'dynamic':
            temp_frame = current_frame
            while temp_frame:
                if identifier_name in temp_frame.locals:
                    temp_frame.set_local(identifier_name, value_to_assign)
                    found_variable_location = True
                    break
                temp_frame = temp_frame.parent_frame
            if not found_variable_location:
                global_var_info = self.global_scope.lookup_current_scope(
                    identifier_name)
                if global_var_info and global_var_info['type'] != 'function':
                    global_var_info['value'] = value_to_assign
                    found_variable_location = True

        if not found_variable_location:
            raise Exception(
                f"Assignment error: Variable '{identifier_name}' not found or cannot be assigned.")

        self._print_call_stack_state(
            f"Assignment: {identifier_name} = {value_to_assign}")

    def visit_CallNode(self, node):
        func_name = node.function_name.name
        func_info = self.global_scope.lookup(func_name)

        if not func_info:
            raise Exception(f"Call error: Function '{func_name}' not defined.")

        if func_info['type'] == 'builtin_function' and func_name == 'print':
            self._handle_print(node.args)
            return

        func_node = func_info['node']

        evaluated_args = [self.visit(arg_node) for arg_node in node.args]

        current_frame = self.call_stack.peek()

        new_frame = ActivationRecord(
            name=func_name,
            scope_type=self.scope_mode,
            parent_frame=current_frame if self.scope_mode == 'dynamic' else None,
            lex_parent_frame=func_info['closure_scope'] if self.scope_mode == 'static' else None
        )

        if len(func_node.params) != len(evaluated_args):
            raise Exception(
                f"Function call error: '{func_name}' expects {len(func_node.params)} arguments, but got {len(evaluated_args)}.")
        for i, param in enumerate(func_node.params):
            new_frame.set_local(param.var_name, evaluated_args[i])

        self.call_stack.push(new_frame)
        self._print_call_stack_state(f"Function Call: {func_name}")

        self.visit(func_node.body)

        self.call_stack.pop()
        self._print_call_stack_state(f"Function Return: {func_name}")

    def visit_IdentifierNode(self, node):
        identifier_name = node.name
        value = None

        if self.scope_mode == 'static':
            current_ar_or_scope = self.call_stack.peek()
            if not current_ar_or_scope:
                current_ar_or_scope = self.global_scope

            temp_scope = current_ar_or_scope
            while temp_scope:
                if isinstance(temp_scope, ActivationRecord) and identifier_name in temp_scope.locals:
                    value = temp_scope.get_local(identifier_name)
                    return value
                elif isinstance(temp_scope, SymbolTable):
                    symbol_info = temp_scope.lookup_current_scope(
                        identifier_name)
                    if symbol_info and symbol_info['type'] != 'function':
                        value = symbol_info['value']
                        return value

                if isinstance(temp_scope, ActivationRecord):
                    temp_scope = temp_scope.lex_parent_frame
                elif isinstance(temp_scope, SymbolTable):
                    temp_scope = temp_scope.parent
                else:
                    break

            raise Exception(
                f"Static Scope Error: Undefined variable '{identifier_name}'.")

        elif self.scope_mode == 'dynamic':
            temp_frame = self.call_stack.peek()
            while temp_frame:
                if identifier_name in temp_frame.locals:
                    value = temp_frame.get_local(identifier_name)
                    return value
                temp_frame = temp_frame.parent_frame

            global_var_info = self.global_scope.lookup_current_scope(
                identifier_name)
            if global_var_info and global_var_info['type'] != 'function':
                value = global_var_info['value']
                return value
            else:
                raise Exception(
                    f"Dynamic Scope Error: Undefined variable '{identifier_name}'.")

    def visit_IntegerNode(self, node):
        return node.value

    def visit_FloatNode(self, node):
        return node.value

    def visit_CharNode(self, node):
        return node.value

    def visit_PrintNode(self, node):
        value = self.visit(node.expression)
        print(f"OUTPUT: {value}")
        self._log_json_state(f"Print statement: {value}", output=value)
        self._print_call_stack_state(f"Print statement: {value}")

    def _handle_print(self, args):
        if not args:
            print("OUTPUT: (empty line)")
            return
        value_to_print = self.visit(args[0])
        print(f"OUTPUT: {value_to_print}")
        # but you can add it if desired.
        # self._print_call_stack_state(f"Built-in Print: {value_to_print}")

    def _print_call_stack_state(self, action):
        self._log_json_state(action)
        console = Console()
        console.rule()
        if action.startswith("Function Call") or action.startswith("Function Return"):
            with Live(refresh_per_second=10, console=console, transient=True) as live:
                for i in range(3):
                    live.update(
                        Panel(f"[bold green]{action}{'.' * (i+1)}", border_style="green"))
                    sleep(0.08)
        else:
            console.rule(f"[bold cyan]{action}")
        stack_panels = []
        for i, ar in enumerate(reversed(self.call_stack.stack)):
            lex_parent_name = ar.lex_parent_frame.name if ar.lex_parent_frame else "None"
            parent_name = ar.parent_frame.name if ar.parent_frame else "None"
            locals_table = Table(
                box=box.MINIMAL, show_header=True, header_style="bold blue")
            locals_table.add_column("Local", style="bold yellow")
            locals_table.add_column("Value", style="white")
            if ar.locals:
                for k, v in ar.locals.items():
                    locals_table.add_row(k, repr(v))
            else:
                locals_table.add_row("(empty)", "-")
            panel = Panel(
                locals_table, title=f"[bold magenta]{ar.name}[/] (type={ar.scope_type}, lex={lex_parent_name}, parent={parent_name})", border_style="magenta")
            stack_panels.append(panel)
        if stack_panels:
            stack_render = Group(*stack_panels)
            console.print(
                Panel(stack_render, title="[bold]Call Stack (Top → Base)", border_style="cyan"))
        else:
            console.print(
                Panel("(empty)", title="Call Stack", border_style="cyan"))
        global_table = Table(title="Global Scope",
                             box=box.SIMPLE, show_lines=True, expand=True)
        global_table.add_column("Name", style="bold yellow")
        global_table.add_column("Value", style="white")
        global_vars_display = {}
        for k, v in self.global_scope.symbols.items():
            if 'value' in v:
                global_vars_display[k] = v['value']
        if global_vars_display:
            for k, v in global_vars_display.items():
                global_table.add_row(k, repr(v))
        else:
            global_table.add_row("(empty)", "-")
        console.print(Panel(
            global_table, title="🌎 [bold blue]Global Scope[/]", border_style="blue", padding=(1, 2)))
        console.rule()

    def visit_BinaryOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if node.op == '+':
            return left + right
        elif node.op == '-':
            return left - right
        else:
            raise Exception(f"Unsupported binary operator: {node.op}")
