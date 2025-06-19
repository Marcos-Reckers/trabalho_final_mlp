import subprocess
from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel

# Caminhos dos arquivos e comandos
EXAMPLE = "src/exemples/exemple5_stack_escopos.pseudo"
INTERPRETER = "src/main.py"

STATIC_CMD = ["python3", INTERPRETER, EXAMPLE, "--static"]
DYNAMIC_CMD = ["python3", INTERPRETER, EXAMPLE, "--dynamic"]

def run_and_capture(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout + ("\n" + result.stderr if result.stderr else "")

def main():
    console = Console()
    console.print("[bold]Executando em modo static...", style="cyan")
    static_output = run_and_capture(STATIC_CMD)
    console.print("[bold]Executando em modo dynamic...", style="magenta")
    dynamic_output = run_and_capture(DYNAMIC_CMD)

    panels = [
        Panel(static_output, title="[bold blue]Static Scope", border_style="blue", padding=(1,2)),
        Panel(dynamic_output, title="[bold magenta]Dynamic Scope", border_style="magenta", padding=(1,2)),
    ]
    console.rule("[bold yellow]Comparação lado a lado: Static x Dynamic")
    console.print(Columns(panels))
    console.rule()

if __name__ == "__main__":
    main()
