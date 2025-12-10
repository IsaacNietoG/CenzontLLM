import fitz  # PyMuPDF
from typing import Dict, Any
import re

def extract_metadata(pdf_path: str) -> Dict[str, Any]:
    doc = fitz.open(pdf_path)
    meta = doc.metadata
    text = doc[0].get_text()
    
    # Extraer DOI del texto si no está en metadata
    doi_match = re.search(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', text, re.I)
    
    # Limpiar y procesar autores
    authors_str = meta.get("author", "")
    authors = [a.strip() for a in authors_str.split(",") if a.strip()] if authors_str else []
    
    # Extraer año de creationDate (formato PDF: "D:YYYYMMDDHHmmss" o similar)
    year = None
    creation_date = meta.get("creationDate", "")
    if creation_date:
        # Buscar año en formato "D:YYYY..." o "YYYY"
        year_match = re.search(r'(\d{4})', creation_date)
        if year_match:
            year = year_match.group(1)
    
    # Si no hay año en metadata, intentar extraerlo del texto
    if not year:
        year_match = re.search(r'\b(19|20)\d{2}\b', text)
        if year_match:
            year = year_match.group(0)
    
    return {
        "title": meta.get("title") or "Unknown",
        "authors": authors,
        "year": year,
        "doi": doi_match.group(0) if doi_match else None,
        "journal": meta.get("producer") or None,
        "page_count": len(doc)
    }
