import typer
from typing import Optional

app = typer.Typer(help="CenzontLLM: PDF → Podcast científico")

@app.command()
def run(
    pdf_path: str = typer.Argument(..., help="Ruta al PDF científico"),
    output: str = typer.Option("podcast.mp3", help="Archivo de salida"),
):
    typer.echo(f"Generando podcast desde {pdf_path}...")
    typer.echo("MVP en construcción... ¡próximamente!")

if __name__ == "__main__":
    app()
