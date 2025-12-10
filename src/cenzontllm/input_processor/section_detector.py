from typing import List, Dict
from unstructured.documents.elements import Title, NarrativeText, ListItem
import re

SECTION_KEYWORDS = {
    "Abstract": ["resumen", "abstract"],
    "Introduction": ["introducción", "introduction"],
    "Methods": ["métodos", "materiales", "methods", "methodology"],
    "Results": ["resultados", "results"],
    "Discussion": ["discusión", "discussion"],
    "Conclusion": ["conclusión", "conclusions"],
    "References": ["referencias", "bibliografía", "references"]
}

def _is_section_header(text: str) -> tuple[bool, str]:
    """
    Detecta si un texto es un encabezado de sección.
    Retorna (es_encabezado, nombre_seccion)
    """
    text_lower = text.lower().strip()
    
    # Verificar si el texto es principalmente un título de sección
    # (corto, sin puntuación final, y contiene palabras clave)
    for sec_name, keywords in SECTION_KEYWORDS.items():
        for keyword in keywords:
            # Buscar palabra clave al inicio del texto o después de un número
            pattern = rf'^(\d+\s*)?{re.escape(keyword)}\s*$'
            if re.match(pattern, text_lower, re.IGNORECASE):
                return True, sec_name
            
            # También verificar si es un título corto que contiene la palabra clave
            # y no tiene mucho contenido adicional
            if keyword in text_lower and len(text.split()) <= 5:
                # Verificar que la palabra clave esté al inicio o después de un número
                words = text_lower.split()
                if keyword in words[:3]:  # En las primeras 3 palabras
                    return True, sec_name
    
    return False, ""

def group_into_sections(elements) -> List[Dict]:
    sections = []
    current_section = {"name": "Preámbulo", "content": "", "elements": []}
    
    for el in elements:
        text = el.text.strip()
        if not text:
            continue
        
        # Verificar si este elemento es un encabezado de sección
        is_header, section_name = _is_section_header(text)
        
        if is_header:
            # Guardar la sección actual si tiene contenido
            if current_section["content"].strip():
                sections.append(current_section)
            
            # Crear nueva sección (sin incluir el texto del encabezado en el contenido)
            current_section = {"name": section_name, "content": "", "elements": []}
        else:
            # Agregar contenido a la sección actual
            current_section["content"] += text + "\n\n"
            current_section["elements"].append(el)
    
    # Agregar la última sección si tiene contenido
    if current_section["content"].strip():
        sections.append(current_section)
    
    return sections
