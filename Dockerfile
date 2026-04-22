FROM pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime
LABEL org.opencontainers.image.source="https://github.com/Mossworks-Labs/mcp-musicgen" \
      org.opencontainers.image.description="GPU service: musicgen" \
      org.opencontainers.image.licenses="MIT"

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

LABEL org.opencontainers.image.source="https://github.com/Mossworks-Labs/mcp-musicgen"
LABEL org.opencontainers.image.description="AI music generation service via AudioCraft"
LABEL org.opencontainers.image.licenses="MIT"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
