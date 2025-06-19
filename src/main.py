import sys
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from scope_resolver import StaticScopeResolver # Only needed for static scope analysis

def run_simulation(file_path, scope_mode, json_log_file=None):
    try:
        with open(file_path, 'r') as f:
            code = f.read()

        print(f"Running simulation for '{file_path}' with {scope_mode.upper()} Scope.\n")

        # 1. Lexical Analysis
        lexer = Lexer(code)
        tokens = lexer.get_tokens()

        # 2. Syntactic Analysis
        parser = Parser(tokens)
        ast = parser.parse_program()

        # 3. Static Scope Resolution (if mode is static)
        if scope_mode == 'static':
            static_resolver = StaticScopeResolver()
            static_resolver.visit(ast)

        # 4. Interpretation
        print(f"--- Starting Interpreter with {scope_mode.upper()} Scope ---")
        interpreter = Interpreter(ast, scope_mode, json_log_file=json_log_file)
        interpreter.interpret()
        print(f"--- Interpreter Finished for {scope_mode.upper()} Scope ---")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python main.py <program_file.pseudo> [--static | --dynamic] [--json-log <logfile.jsonl>]")
        sys.exit(1)

    file_path = sys.argv[1]
    scope_flag = sys.argv[2]
    json_log_file = None
    if len(sys.argv) > 3 and sys.argv[3] == '--json-log' and len(sys.argv) > 4:
        json_log_file = sys.argv[4]

    if scope_flag == '--static':
        scope_mode = 'static'
    elif scope_flag == '--dynamic':
        scope_mode = 'dynamic'
    else:
        print("Invalid scope flag. Use --static or --dynamic.")
        sys.exit(1)

    run_simulation(file_path, scope_mode, json_log_file=json_log_file)