from typing import List, Dict
from unstructured.documents.elements import Title, NarrativeText, ListItem

SECTION_KEYWORDS = {
    "Abstract": ["resumen", "abstract"],
    "Introduction": ["introducción", "introduction"],
    "Methods": ["métodos", "materiales", "methods", "methodology"],
    "Results": ["resultados", "results"],
    "Discussion": ["discusión", "discussion"],
    "Conclusion": ["conclusión", "conclusions"],
    "References": ["referencias", "bibliografía", "references"]
}

def group_into_sections(elements) -> List[Dict]:
    sections = []
    current_section = {"name": "Preámbulo", "content": "", "elements": []}
    
    for el in elements:
        text = el.text.strip()
        if not text:
            continue
            
        # Detectar sección por título
        matched = False
        for sec_name, keywords in SECTION_KEYWORDS.items():
            if any(k.lower() in text.lower() for k in keywords):
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {"name": sec_name, "content": "", "elements": []}
                matched = True
                break
        
        current_section["content"] += text + "\n\n"
        current_section["elements"].append(el)
    
    if current_section["content"]:
        sections.append(current_section)
    
    return sections
