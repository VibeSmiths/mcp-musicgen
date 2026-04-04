FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl && \
    rm -rf /var/lib/apt/lists/*

# Pin av, torch, torchaudio to prevent audiocraft from downgrading torch
COPY constraints.txt .
RUN pip install --no-cache-dir numpy && \
    pip install --no-cache-dir -c constraints.txt audiocraft fastapi uvicorn[standard]

COPY main.py .

ENV MODELS_DIR=/app/models
EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
