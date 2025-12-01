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

@app.command()
def input(pdf: str = typer.Argument(..., help="Ruta al PDF")):
    from cenzontllm.input_processor.pipeline import process_pdf
    result = process_pdf(pdf, "paper_content.json")
    typer.echo(f"Listo! {len(result['sections'])} secciones extraídas.")

if __name__ == "__main__":
    app()
