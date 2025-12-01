FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    python3-pip python3-dev git curl ffmpeg poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .
RUN pip3 install poetry && poetry config virtualenvs.create false

COPY . .

RUN poetry install --only main

CMD ["python", "-m", "src.cenzontllm.main", "--help"]

