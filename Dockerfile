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

COPY . .

# Entrypoint
ENTRYPOINT ["python3", "-m", "src.cenzontllm.main"]
