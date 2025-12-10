from .base import BaseAgent
from ..prompts import GUEST_RESPONSE_PROMPT
from typing import Dict
import json

class GuestAgent(BaseAgent):
    name = "guest"

    def respond(self, question: str, history: str, guest_profile: Dict, paper: Dict) -> str:
        # Formatear el paper de manera legible para el prompt
        paper_summary = self._format_paper_for_prompt(paper)
        
        prompt = GUEST_RESPONSE_PROMPT.format(
            name=guest_profile["name"], 
            age=guest_profile["age"], 
            accent=guest_profile["accent"],
            bio=guest_profile["bio"], 
            style=guest_profile["style"], 
            question=question, 
            history=history,
            paper_content=paper_summary
        )
        return self.invoke(prompt)

    def _format_paper_for_prompt(self, paper: Dict) -> str:
        """
        Formatea el paper en un formato legible para el prompt del LLM.
        Incluye metadata, secciones principales y figuras.
        Prioriza secciones técnicas importantes con más contenido.
        """
        lines = []
        
        # Metadata
        if "metadata" in paper:
            meta = paper["metadata"]
            lines.append("=== METADATA DEL PAPER ===")
            if meta.get("title"):
                lines.append(f"Título: {meta['title']}")
            if meta.get("authors"):
                authors_str = ", ".join(meta["authors"]) if isinstance(meta["authors"], list) else meta["authors"]
                lines.append(f"Autores: {authors_str}")
            if meta.get("year"):
                lines.append(f"Año: {meta['year']}")
            if meta.get("doi"):
                lines.append(f"DOI: {meta['doi']}")
            lines.append("")
        
        # Secciones - con límites dinámicos según importancia
        if "sections" in paper and paper["sections"]:
            lines.append("=== CONTENIDO DEL PAPER ===")
            
            # Secciones técnicas críticas que necesitan más contenido
            high_priority_sections = {
                "Methods", "Methodology", "Architecture", "Model", "Implementation",
                "Results", "Experiments", "Evaluation", "Analysis",
                "Discussion", "Background", "Related Work"
            }
            
            # Secciones que pueden ser más cortas
            low_priority_sections = {
                "Abstract", "Introduction", "Conclusion", "References", 
                "Acknowledgments", "Appendix"
            }
            
            for section in paper["sections"]:
                section_name = section.get("name", "Sin nombre")
                section_content = section.get("content", "").strip()
                
                if not section_content:
                    continue
                
                # Determinar límite según importancia de la sección
                if any(priority in section_name for priority in high_priority_sections):
                    # Secciones técnicas importantes: hasta 2000 caracteres
                    char_limit = 2000
                elif any(priority in section_name for priority in low_priority_sections):
                    # Secciones menos técnicas: hasta 800 caracteres
                    char_limit = 800
                else:
                    # Secciones intermedias: hasta 1500 caracteres
                    char_limit = 1500
                
                # Incluir contenido completo si es corto, o preview si es largo
                if len(section_content) <= char_limit:
                    content_preview = section_content
                else:
                    # Tomar primeros caracteres pero intentar cortar en un punto lógico
                    content_preview = section_content[:char_limit]
                    # Intentar cortar en el último punto o salto de línea
                    last_period = content_preview.rfind('.')
                    last_newline = content_preview.rfind('\n')
                    cut_point = max(last_period, last_newline)
                    if cut_point > char_limit * 0.7:  # Si encontramos un buen punto de corte
                        content_preview = content_preview[:cut_point + 1]
                    content_preview += "..."
                
                lines.append(f"\n--- {section_name} ---")
                lines.append(content_preview)
            lines.append("")
        
        # Figuras (si hay)
        if "figures" in paper and paper["figures"]:
            lines.append("=== FIGURAS ===")
            for fig in paper["figures"]:
                if fig.get("description"):
                    lines.append(f"- {fig['description']}")
            lines.append("")
        
        return "\n".join(lines)

    def _call_llm(self, prompt: str) -> str:
        return "Respuesta del guest from LLM"
