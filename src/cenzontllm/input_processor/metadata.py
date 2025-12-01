import fitz  # PyMuPDF
from typing import Dict, Any

def extract_metadata(pdf_path: str) -> Dict[str, Any]:
    doc = fitz.open(pdf_path)
    meta = doc.metadata
    text = doc[0].get_text()
    
    # Extraer DOI del texto si no está en metadata
    import re
    doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', text, re.I)
    
    return {
        "title": meta.get("title") or "Unknown",
        "authors": meta.get("author", "").split(","),
        "year": meta.get("creationDate", "")[:4] or None,
        "doi": doi_match.group(0) if doi_match else None,
        "journal": meta.get("producer") or None,
        "page_count": len(doc)
    }
