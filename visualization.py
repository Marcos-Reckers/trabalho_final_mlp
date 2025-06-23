"""
Este módulo implementa a visualização lado a lado de execuções com escopo estático 
e dinâmico. Carrega logs JSON gerados pelo interpretador e os reproduz de forma 
sincronizada, mostrando o estado da pilha de chamadas e variáveis globais em 
cada etapa da execução. Permite análise detalhada das diferenças entre os dois 
modos de escopo através de uma interface visual colorida no terminal.
"""

import json
from rich.console import Console, Group
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich import box
import time


def load_log(logfile):
    with open(logfile, 'r') as f:
        return [json.loads(line) for line in f if line.strip()]


def render_state(entry, color):
    action = entry['action']
    stack = entry['call_stack']
    global_scope = entry['global_scope']
    output = entry.get('output')
    stack_panels = []
    for ar in reversed(stack):
        locals_table = Table(
            box=box.MINIMAL, show_header=True, header_style="bold blue")
        locals_table.add_column("Local", style="bold yellow")
        locals_table.add_column("Value", style="white")
        if ar['locals']:
            for k, v in ar['locals'].items():
                locals_table.add_row(k, repr(v))
        else:
            locals_table.add_row("(empty)", "-")
        panel = Panel(
            locals_table, title=f"[bold magenta]{ar['name']}[/] (type={ar['scope_type']}, lex={ar['lex_parent']}, parent={ar['parent']})", border_style="magenta", padding=(0, 1))
        stack_panels.append(panel)
    if stack_panels:
        stack_render = Group(*stack_panels)
        stack_panel = Panel(
            stack_render, title="[bold]Call Stack (Top → Base)", border_style="cyan", padding=(0, 1))
    else:
        stack_panel = Panel("(empty)", title="Call Stack",
                            border_style="cyan", padding=(0, 1))
    global_table = Table(title="Global Scope",
                         box=box.SIMPLE, show_lines=True, expand=True)
    global_table.add_column("Name", style="bold yellow")
    global_table.add_column("Value", style="white")
    if global_scope:
        for k, v in global_scope.items():
            global_table.add_row(k, repr(v))
    else:
        global_table.add_row("(empty)", "-")
    global_panel = Panel(
        global_table, title="🌎 [bold blue]Global Scope[/]", border_style="blue", padding=(0, 1))
    group_items = [f"[b]{action}[/b]"]
    if output is not None:
        group_items.append(f"[bold green]OUTPUT:[/] [white]{output}[/]")
    group_items.extend([stack_panel, global_panel])
    return Panel(
        Group(*group_items),
        border_style=color, padding=(0, 1), width=80
    )


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Visualiza execuções static e dynamic lado a lado com cores.")
    parser.add_argument('--static-log', required=True,
                        help='Arquivo de log JSONL do modo static')
    parser.add_argument('--dynamic-log', required=True,
                        help='Arquivo de log JSONL do modo dynamic')
    parser.add_argument('--delay', type=float, default=1.0,
                        help='Delay entre etapas (segundos)')
    args = parser.parse_args()

    static_entries = load_log(args.static_log)
    dynamic_entries = load_log(args.dynamic_log)
    n = min(len(static_entries), len(dynamic_entries))
    console = Console()
    min_width = 170
    if console.size.width < min_width:
        console.print(
            f"[bold red]Aumente a largura do terminal para pelo menos {min_width} colunas para ver lado a lado! (atual: {console.size.width})[/]")
        time.sleep(3)
    for i in range(n):
        panels = [
            render_state(static_entries[i], 'blue'),
            render_state(dynamic_entries[i], 'magenta')
        ]
        console.clear()
        console.rule(f"[bold yellow]Etapa {i+1}/{n}")
        console.print(Columns(panels, expand=True, equal=True))
        console.rule()
        time.sleep(args.delay)


if __name__ == "__main__":
    main()
