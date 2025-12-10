import json
from pathlib import Path
from .metadata import extract_metadata
from .extractor import extract_elements
from .section_detector import group_into_sections
from .figure_captioner import generate_figure_captions

def process_pdf(pdf_path: str, output_json: str = None) -> dict:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(pdf_path)
    
    print("Extracting metadata...")
    metadata = extract_metadata(str(pdf_path))
    
    print("Partitioning PDF with unstructured...")
    elements = extract_elements(str(pdf_path))
    
    print("Grouping into sections...")
    sections = group_into_sections(elements)
    
    # Extraer imágenes (si hay) (feature con GPU, WIP)
    image_elements = [e for e in elements if hasattr(e, "image_path") and e.image_path]
    figure_captions = generate_figure_captions([e.image_path for e in image_elements])
    
    result = {
        "metadata": metadata,
        "sections": [
            {"name": s["name"], "content": s["content"].strip()}
            for s in sections
        ],
        "figures": figure_captions,
        "raw_element_count": len(elements)
    }
    
    if output_json:
        Path(output_json).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"paper_content.json guardado en {output_json}")
    
    return result
