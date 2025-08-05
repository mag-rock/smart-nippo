"""Hello World command for testing basic CLI functionality"""


import typer
from rich.console import Console

console = Console()


def hello(
    name: str | None = typer.Argument(None, help="挨拶する相手の名前"),
    count: int = typer.Option(1, "--count", "-c", help="挨拶の回数"),
    japanese: bool = typer.Option(False, "--japanese", "-j", help="日本語で挨拶"),
) -> None:
    """Hello World コマンド - CLIの基本動作をテストします"""

    if japanese:
        greeting = "こんにちは" if name else "こんにちは、世界！"
        if name:
            greeting = f"こんにちは、{name}さん！"
    else:
        greeting = f"Hello, {name}!" if name else "Hello, World!"

    for i in range(count):
        if count > 1:
            console.print(f"{i+1}: {greeting}", style="bold green")
        else:
            console.print(greeting, style="bold green")
