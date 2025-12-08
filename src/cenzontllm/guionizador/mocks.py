from .prompts import HOST_INITIAL_PROMPT, GUEST_RESPONSE_PROMPT, HOST_EVALUATION_PROMPT, WRITER_PROMPT

MOCK_HOST_INITIAL = {
    "guests": [{"name": "Dr. Luis Ramírez", "age": 50, "accent": "mexicano", "bio": "Físico teórico", "style": "académico accesible"}],
    "outline": ["1. Problema", "2. Contribución", "3. Arquitectura", "4. Resultados", "5. Conclusiones"]
}

MOCK_GUEST_RESPONSE = "Como Dr. Luis Ramírez, con acento mexicano: El Transformer es revolucionario porque..."

MOCK_HOST_EVALUATION = "COVERAGE:\n1. [OK]\n2. [OK]\n3. [FALTA]\n\nNUEVAS_PREGUNTAS:\n- ¿Cómo funciona self-attention?\n- ¿Limitaciones?"

MOCK_WRITER_GUION = """
**Ana [enthusiastic]:** ¡Bienvenidos a CenzontLLM!

**Dr. Luis Ramírez [serious_explanatory]:** El paper propone...

[SFX: música transición]
"""

def mock_invoke(agent_name: str, input_data: str) -> str:
    if "initial" in agent_name:
        return json.dumps(MOCK_HOST_INITIAL)
    if "response" in agent_name:
        return MOCK_GUEST_RESPONSE
    if "evaluation" in agent_name:
        return MOCK_HOST_EVALUATION
    if "writer" in agent_name:
        return MOCK_WRITER_GUION
    return "Mock response"
