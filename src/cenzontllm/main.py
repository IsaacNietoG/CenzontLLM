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
def guion(
    pdf_json: str = typer.Argument(..., help="Ruta al paper_content.json"),
    mock: bool = typer.Option(True, "--mock", "--no-mock", help="Usar respuestas mock (rápido) o LLM real"),
):
    """
    Genera el guion de podcast.
    Por defecto usamos modo MOCK para pruebas locales rápidas.
    """
    import os
    os.environ["RUN_MODE"] = "mock" if mock else "groq"  # forzar el modo

    from .guionizador.graph import create_podcast_graph

    typer.echo("Iniciando generación del guion de podcast...")
    result = create_podcast_graph(pdf_json)

    output_file = "guion_podcast.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result["final_script"])

    typer.echo(f"¡GUIÓN GENERADO! → {output_file}")
    typer.echo(f"Duración estimada: ~{result.get('estimated_minutes', 5)} minutos")
    typer.echo("Para usar LLM real: guion paper_content.json --no-mock")

@app.command()
def input(pdf: str = typer.Argument(..., help="Ruta al PDF")):
    from .input_processor.pipeline import process_pdf
    result = process_pdf(pdf, "paper_content.json")
    typer.echo(f"Listo! {len(result['sections'])} secciones extraídas.")

if __name__ == "__main__":
    app()
