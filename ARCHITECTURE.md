# Arquitectura de CenzontLLM

Este documento describe la arquitectura técnica del sistema CenzontLLM, un framework para convertir artículos científicos (PDF) en podcasts conversacionales usando LLMs y sistemas multi-agente.

---

## Tabla de Contenidos

1. [Visión General](#visión-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Componentes Principales](#componentes-principales)
4. [Flujo de Datos](#flujo-de-datos)
5. [Sistema Multi-Agente](#sistema-multi-agente)
6. [Workflow LangGraph](#workflow-langgraph)
7. [Decisiones de Diseño](#decisiones-de-diseño)
8. [Extensiones Futuras](#extensiones-futuras)

---

## Visión General

CenzontLLM sigue una arquitectura modular de pipeline con tres etapas principales:

```
PDF → Input Processor → Guionizador (Multi-Agent) → TTS → Audio
```

Cada etapa es independiente y puede ejecutarse por separado, facilitando el desarrollo, testing y mantenimiento.

### Principios de Diseño

- **Modularidad**: Cada componente tiene responsabilidades claras y bien definidas
- **Extensibilidad**: Fácil agregar nuevos agentes, procesadores o integraciones
- **Testabilidad**: Modo mock para desarrollo sin dependencias externas
- **Escalabilidad**: Diseño preparado para extensiones a procesamiento paralelo y cloud

---

## Arquitectura del Sistema

### Diagrama de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                         CenzontLLM CLI                          │
│                    (src/cenzontllm/main.py)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┴────────────┐
                │                         │
        ┌───────▼────────┐      ┌────────▼────────┐
        │ Input Processor │      │   Guionizador   │
        │                 │      │  (Multi-Agent)  │
        └───────┬────────┘      └────────┬────────┘
                │                         │
                │                         │
    ┌───────────┴──────────┐    ┌────────┴────────┐
    │                      │    │                 │
┌───▼────┐  ┌───────────┐  │    │  ┌───────────┐  │
│Metadata│  │Extractor  │  │    │  │  Host     │  │
│Extract │  │(unstruct.)│  │    │  │  Agent    │  │
└────────┘  └───────────┘  │    │  └───────────┘  │
                           │    │                 │
┌──────────┐  ┌──────────┐ │    │  ┌───────────┐  │
│Section   │  │Figure    │ │    │  │  Guest    │  │
│Detector  │  │Captioner │ │    │  │  Agent    │  │
└──────────┘  └──────────┘ │    │  └───────────┘  │
                           │    │                 │
                           │    │  ┌───────────┐  │
                           │    │  │  Writer   │  │
                           │    │  │  Agent    │  │
                           │    │  └───────────┘  │
                           │    │                 │
                           │    └────────┬────────┘
                           │             │
                           │    ┌────────▼────────┐
                           │    │  LangGraph      │
                           │    │  Workflow       │
                           │    └─────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
         ┌──────▼──────┐      ┌──────▼──────┐
         │   Groq API  │      │   Mock Mode │
         │  (LLM Real) │      │  (Testing)  │
         └─────────────┘      └─────────────┘
```

---

## Componentes Principales

### 1. Input Processor (`src/cenzontllm/input_processor/`)

Responsable de extraer y estructurar el contenido del PDF científico.

#### 1.1 Pipeline Principal (`pipeline.py`)

Orquesta el procesamiento completo desde la fuente (PDF por ahora):

```python
process_pdf(pdf_path: str, output_json: str = None) -> dict
```

**Flujo interno:**
1. Extracción de metadatos
2. Particionado del PDF
3. Agrupación en secciones
4. Extracción de figuras (opcional)

**Salida:** `paper_content.json` con estructura:
```json
{
  "metadata": {...},
  "sections": [...],
  "figures": [...],
  "raw_element_count": N
}
```

#### 1.2 Extractor de Metadatos (`metadata.py`)

**Tecnología:** PyMuPDF (fitz)

**Extrae:**
- Título del paper
- Autores (lista)
- Año de publicación
- DOI (mediante regex)
- Journal/Producer
- Número de páginas

**Método:** `extract_metadata(pdf_path: str) -> Dict[str, Any]`

#### 1.3 Extractor de Elementos (`extractor.py`)

**Tecnología:** Unstructured (`partition_pdf`)

**Configuración:**
- `strategy="hi_res"`: Máxima calidad de extracción
- `infer_table_structure=True`: Detecta tablas
- `languages=["spa", "eng"]`: Soporte bilingüe
- `extract_images_in_pdf=True`: Extrae imágenes

**Salida:** Lista de elementos estructurados (Title, NarrativeText, ListItem, etc.)

#### 1.4 Detector de Secciones (`section_detector.py`)

**Algoritmo:** Búsqueda por palabras clave

**Secciones detectadas:**
- Abstract / Resumen
- Introduction / Introducción
- Methods / Métodos
- Results / Resultados
- Discussion / Discusión
- Conclusion / Conclusión
- References / Referencias

**Método:** `group_into_sections(elements) -> List[Dict]`

Agrupa elementos consecutivos bajo la misma sección hasta encontrar un nuevo título.

#### 1.5 Captioner de Figuras (`figure_captioner.py`)

**Estado:** Placeholder (WIP)

**Plan futuro:** Integración con modelos de visión (LLaVA, GPT-4V) para generar descripciones automáticas de figuras. Esto con el objetivo de enriquecer la información a la que puede acceder el guionizador

---

### 2. Guionizador (`src/cenzontllm/guionizador/`)

Sistema multi-agente que genera guiones de podcast conversacionales. Inspirado en el sistema multiagentes de PodcastLLM

#### 2.1 Arquitectura de Agentes

Todos los agentes heredan de `BaseAgent` que proporciona:

- **Abstracción de LLM**: Maneja modo mock vs. real
- **Método `invoke()`**: Punto de entrada unificado
- **Configuración centralizada**: Usa `settings` para parámetros

```python
class BaseAgent(ABC):
    name: str = "base"
    
    def invoke(self, input_data: Any) -> str:
        # Lógica de mock vs. Groq
        ...
    
    @abstractmethod
    def _call_llm(self, input_data: Any) -> str:
        pass
```

#### 2.2 HostAgent (`agents/host.py`)

**Responsabilidades:**
1. Generar personalidades de invitados
2. Crear outline estructurado del podcast
3. Evaluar cobertura de la conversación

**Métodos principales:**

- `generate_personalities_and_outline(paper: Dict) -> Dict`
  - Input: Paper completo (JSON)
  - Output: `{"guests": [...], "outline": [...]}`
  - Usa `HOST_INITIAL_PROMPT`

- `evaluate_coverage(conversation: str, outline: str, ...) -> str`
  - Evalúa qué temas se han cubierto
  - Genera preguntas de seguimiento si es necesario
  - Usa `HOST_EVALUATION_PROMPT`

**Personalidades generadas:**
- Nombre, edad, acento regional
- Bio profesional
- Estilo de habla (académico, accesible, técnico)
- Nivel de expertise

#### 2.3 GuestAgent (`agents/guest.py`)

**Responsabilidades:**
- Responder preguntas como experto
- Mantener consistencia de personalidad
- Generar respuestas científicamente rigurosas pero accesibles

**Método principal:**

- `respond(question: str, history: str, guest_profile: Dict) -> str`
  - Input: Pregunta, historial de conversación, perfil del invitado
  - Output: Respuesta en primera persona del personaje
  - Usa `GUEST_RESPONSE_PROMPT`

**Características:**
- Respuestas contextualizadas (usa historial)
- Personalidad consistente (nombre, acento, estilo)
- Puede incluir muletillas según personalidad

#### 2.4 WriterAgent (`agents/writer.py`)

**Responsabilidades:**
- Convertir conversación raw en guion profesional
- Añadir anotaciones de voz y efectos
- Balancear duración objetivo

**Método principal:**

- `write(conversation: str, guests: List[dict], target_minutes: int) -> str`
  - Input: Conversación completa, lista de invitados, duración objetivo
  - Output: Guion en Markdown con formato profesional
  - Usa `WRITER_PROMPT`

**Formato de salida:**
```markdown
**Ana [enthusiastic]:** ¡Bienvenidos a CenzontLLM!

**Dr. Luis Ramírez [serious_explanatory]:** El paper propone...

[SFX: música transición]
```

**Incluye:**
- Intro y outro cautivadores
- Anotaciones de emoción `[enthusiastic]`, `[surprised]`, etc.
- Efectos de sonido `[SFX: ...]`
- Pausas estratégicas
- Descripciones de voz para cada personaje

---

### 3. Workflow LangGraph (`graph.py`)

Orquesta la interacción entre agentes usando LangGraph.

#### 3.1 Estado del Workflow

```python
class PodcastState(TypedDict):
    paper: Dict              # Paper completo (JSON)
    guests: List[Dict]       # Personalidades de invitados
    outline: List[str]       # Preguntas/temas a cubrir
    conversation: List[Dict[str, str]]  # Historial de diálogos
    round: int               # Ronda actual
    final_script: str        # Guion final generado
    should_end: bool         # Flag de terminación
```

#### 3.2 Nodos del Grafo

```
┌─────────┐
│  init   │  ← Entry point
└────┬────┘
     │
     ▼
┌─────────┐
│ respond │  ← Invitados responden preguntas
└────┬────┘
     │
     ▼
┌─────────┐
│evaluate │  ← Host evalúa cobertura
└────┬────┘
     │
     ├─── should_end? ──┐
     │                  │
     │ NO               │ YES
     │                  │
     ▼                  ▼
┌─────────┐      ┌──────────┐
│ respond │      │ finalize │
└─────────┘      └────┬─────┘
                      │
                      ▼
                    END
```

#### 3.3 Flujo Detallado

**1. Nodo `init` (`init_host`)**
- Carga el paper desde JSON
- HostAgent genera personalidades y outline
- Inicializa conversación con saludo
- Retorna estado inicial completo

**2. Nodo `respond` (`guests_respond`)**
- Itera sobre cada pregunta del outline
- Para cada pregunta, cada invitado genera respuesta
- Host intercala comentarios ("¡Perfecto!")
- Actualiza `conversation` con nuevos turnos

**3. Nodo `evaluate` (`host_evaluate`)**
- HostAgent evalúa cobertura del outline
- Decide si continuar o terminar
- Actualiza `should_end` y opcionalmente `outline` con nuevas preguntas

**4. Nodo `finalize` (`writer_finalize`)**
- WriterAgent convierte conversación en guion
- Aplica formato profesional
- Genera `final_script`

#### 3.4 Condiciones de Terminación

El workflow termina cuando:
- `should_end == True` (evaluado por HostAgent)
- Se alcanza `MAX_REPLICA_ROUNDS` (configurable)

---

## Flujo de Datos

### Pipeline Completo

```
1. PDF Input
   │
   ▼
2. Input Processor
   ├─→ Metadata Extraction (PyMuPDF)
   ├─→ PDF Partitioning (Unstructured)
   ├─→ Section Detection (Keyword-based)
   └─→ Figure Extraction (Placeholder)
   │
   ▼
3. paper_content.json
   {
     "metadata": {...},
     "sections": [...],
     "figures": [...]
   }
   │
   ▼
4. Guionizador (LangGraph)
   ├─→ init: Genera personalidades + outline
   ├─→ respond: Invitados responden (iterativo)
   ├─→ evaluate: Host evalúa cobertura
   └─→ finalize: Writer genera guion
   │
   ▼
5. guion_podcast.md
   │
   ▼
6. TTS (Futuro)
   └─→ podcast.mp3
```

### Flujo de Datos en el Workflow

```
Estado Inicial (vacío)
    │
    ▼
init_host()
    │
    ├─→ paper (cargado)
    ├─→ guests (generados por HostAgent)
    ├─→ outline (generado por HostAgent)
    └─→ conversation (inicializado)
    │
    ▼
guests_respond() [Ronda 1]
    │
    ├─→ Para cada pregunta en outline:
    │   ├─→ GuestAgent.respond() → respuesta
    │   └─→ Host intercala comentario
    │
    └─→ conversation (actualizado)
    │
    ▼
host_evaluate()
    │
    ├─→ HostAgent.evaluate_coverage()
    ├─→ should_end = True/False
    └─→ outline (opcionalmente actualizado)
    │
    ├─→ should_end == False ──┐
    │                         │
    └─→ should_end == True    │
                              │
                              ▼
                    guests_respond() [Ronda 2]
                              │
                              ▼
                    host_evaluate()
                              │
                              ▼
                    (loop hasta should_end == True)
                              │
                              ▼
                    writer_finalize()
                              │
                              └─→ final_script
```

---

## Sistema Multi-Agente

### Patrón de Diseño

CenzontLLM implementa un patrón de **agentes especializados** donde cada agente tiene un rol específico:

- **HostAgent**: Moderador y coordinador
- **GuestAgent(s)**: Expertos que responden preguntas
- **WriterAgent**: Editor que formatea el contenido final

### Comunicación entre Agentes

Los agentes no se comunican directamente. La comunicación se realiza a través del **estado compartido** (`PodcastState`):

1. **HostAgent** escribe en `guests` y `outline`
2. **GuestAgent** lee `outline`, `conversation` y el contenido del paper, escribe en `conversation`
3. **HostAgent** lee `conversation` para evaluar
4. **WriterAgent** lee `conversation` y `guests` para generar guion

### Ventajas de este Diseño

- **Desacoplamiento**: Agentes independientes, fáciles de testear
- **Escalabilidad**: Fácil agregar más invitados o roles
- **Trazabilidad**: Estado centralizado permite debugging
- **Flexibilidad**: Fácil cambiar lógica de un agente sin afectar otros

---

## Decisiones de Diseño

### 1. ¿Por qué LangGraph?

**Razones:**
- **Workflows complejos**: Necesitamos loops condicionales y estado compartido
- **Debugging**: Visualización del flujo de ejecución
- **Extensibilidad**: Fácil agregar nuevos nodos o condiciones
- **Integración**: Compatible con LangChain y otros frameworks

### 2. ¿Por qué Modo Mock?

**Razones:**
- **Desarrollo rápido**: No requiere API keys durante desarrollo
- **Testing**: Permite probar lógica sin costos
- **CI/CD**: Tests pueden ejecutarse sin dependencias externas
- **Debugging**: Respuestas predecibles facilitan debugging

**Implementación:**
- Respuestas hardcodeadas en `mocks.py`
- Activado por defecto (`RUN_MODE=mock`)
- Fácil desactivar con `--no-mock` flag

### 3. ¿Por qué Groq API?

**Razones:**
- **Velocidad**: Inferencia muy rápida (ideal para desarrollo iterativo)
- **Costo**: Más económico que OpenAI para este caso de uso. Con créditos gratuitos que fueron muy útiles para las pruebas iniciales.
- **Modelos**: Acceso a Llama 3.3 70B, modelos de alta calidad
- **API simple**: Fácil integración

**Alternativas futuras:**
- **Ollama**: Para modelos locales (ya planificado)
- **OpenAI**: Si se necesita GPT-4 para casos complejos
- **Anthropic**: Claude para mejor razonamiento

### 4. ¿Por qué Unstructured para PDFs?

**Razones:**
- **Calidad**: Extracción de alta calidad con `hi_res` strategy
- **Estructura**: Detecta automáticamente títulos, párrafos, listas
- **Tablas**: Soporte para extracción de tablas
- **Imágenes**: Extracción de imágenes integrada
- **Multilingüe**: Soporte para español e inglés

**Limitaciones:**
- Requiere dependencias pesadas (Tesseract, etc.)
- Procesamiento más lento que alternativas simples
- **Solución**: Dockerfile pre-configurado

### 5. ¿Por qué Typer para CLI?

**Razones:**
- **Moderno**: Basado en type hints de Python
- **Auto-documentación**: Genera help automático
- **Validación**: Validación de tipos integrada
- **Rich**: Integración con Rich para output bonito

---

## Extensiones Futuras

### 1. Text-to-Speech (TTS)

**Arquitectura planificada:**

```
guion_podcast.md
    │
    ▼
Parser de Guion
    ├─→ Extrae diálogos por personaje
    ├─→ Extrae anotaciones de emoción
    └─→ Extrae efectos de sonido
    │
    ▼
TTS Engine (por personaje)
    ├─→ Selecciona voz según acento
    ├─→ Aplica emoción según anotación
    └─→ Genera audio segmentado
    │
    ▼
Post-procesamiento
    ├─→ Mezcla de voces
    ├─→ Añade música de fondo
    ├─→ Añade efectos de sonido
    └─→ Normalización de audio
    │
    ▼
podcast.mp3
```

**Tecnologías candidatas:**
- **Coqui TTS**: Open-source, soporte para español
- **ElevenLabs**: Calidad alta, API comercial
- **Azure TTS**: Buena calidad, múltiples voces en español

### 2. Captioning de Figuras

**Arquitectura planificada:**

```
Figura extraída (imagen)
    │
    ▼
Modelo de Visión
    ├─→ LLaVA (local, GPU)
    ├─→ GPT-4V (API)
    └─→ CLIP + LLM (híbrido)
    │
    ▼
Descripción generada
    │
    └─→ Integrada en guion como referencia
```

### 3. Integración con Ollama

**Arquitectura planificada:**

```
BaseAgent.invoke()
    │
    ├─→ RUN_MODE == "mock" → mock_invoke()
    ├─→ RUN_MODE == "groq" → Groq API
    └─→ RUN_MODE == "ollama" → Ollama local
```

**Ventajas:**
- Sin costos de API
- Privacidad total
- Control sobre el modelo

### 4. Pipeline Completo (`run` command)

**Implementación planificada:**

```python
@app.command()
def run(pdf_path: str, output: str = "podcast.mp3"):
    # 1. Procesar PDF
    paper_json = process_pdf(pdf_path, "paper_content.json")
    
    # 2. Generar guion
    script = create_podcast_graph("paper_content.json")
    
    # 3. Convertir a audio
    audio = tts_engine.generate(script["final_script"])
    
    # 4. Post-procesar
    final_audio = post_process(audio)
    
    # 5. Guardar
    final_audio.export(output)
```

### 5. Mejoras en el Workflow

**Planificadas:**
- **Memoria persistente**: Guardar estado entre ejecuciones
- **Checkpointing**: Poder reanudar desde un punto específico
- **Paralelización**: Múltiples invitados responden en paralelo
- **Feedback loop**: Permitir edición manual del guion y regeneración

---

## Consideraciones de Rendimiento

### Cuellos de Botella Actuales

1. **Procesamiento de PDF**: Unstructured puede ser lento en PDFs grandes
   - **Solución**: Procesamiento asíncrono, caching

2. **LLM Calls**: Cada respuesta de invitado requiere una llamada API
   - **Solución**: Batching, caching de respuestas similares

### Optimizaciones Futuras

- **Caching**: Cachear respuestas de LLM para preguntas similares
- **Streaming**: Generar guion de forma incremental
- **Paralelización**: Procesar múltiples papers simultáneamente.
- **GPU**: Usar GPU para procesamiento de imágenes y TTS

---

## Seguridad y Privacidad

### Consideraciones Actuales

- **API Keys**: Almacenadas en `.env` (no versionado)
- **Datos**: PDFs procesados localmente (no se envían a servicios externos excepto Groq)
- **Groq API**: Envía contenido del paper a Groq (revisar términos de servicio)

---

## Conclusión

La arquitectura de CenzontLLM está diseñada para ser:

- **Modular**: Componentes independientes y reutilizables
- **Extensible**: Fácil agregar nuevas funcionalidades
- **Mantenible**: Código claro y bien estructurado
- **Escalable**: Preparado para crecimiento futuro

El sistema actual es funcional para generar guiones de podcast desde PDFs científicos, y está preparado para la integración de TTS y otras mejoras planificadas.

## Áreas de mejora generales

- **Perfeccionamiento de prompts**
- **Interfaz gráfica (GUI)**
- **Curación de la selección de modelos para las necesidades de cada agente.**
- **Preparaciones para correr framework en local**
- **Agregar más tipos de fuentes.**

---

**Última actualización**: Diciembre 2025  
**Versión del documento**: 1.0

