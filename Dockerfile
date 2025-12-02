FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip python3-dev git curl ffmpeg poppler-utils tesseract-ocr libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir poetry

WORKDIR /app

# 1. Copiar archivos de dependencias
COPY pyproject.toml poetry.lock* ./

# 2. Instalar dependencias
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-root --no-interaction --no-ansi

# 2.1 unstructured no descarga chido NTLK, entonces tocó a manita
RUN python3 -c "\
import nltk, os; \
os.makedirs('/usr/local/share/nltk_data/tokenizers', exist_ok=True); \
os.makedirs('/usr/local/share/nltk_data/taggers', exist_ok=True); \
nltk.download('punkt_tab', download_dir='/usr/local/share/nltk_data', quiet=True); \
nltk.download('averaged_perceptron_tagger_eng', download_dir='/usr/local/share/nltk_data', quiet=True); \
print('NLTK data descargado correctamente')\
"

COPY . .

# Entrypoint
ENTRYPOINT ["python3", "-m", "src.cenzontllm.main"]
