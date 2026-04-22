# mcp-musicgen

GPU service for text-to-music generation via Meta AudioCraft (CUDA + ROCm).

Part of the [CRAFT](https://github.com/Mossworks-Labs/craft) content studio.

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Returns GPU availability and status |
| `/generate` | POST | Generate music from a text prompt |

### Generate

```bash
curl -X POST http://localhost:8001/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "upbeat acoustic guitar", "duration": 10, "model_size": "small"}' \
  --output music.wav
```

**Parameters:**
- `prompt` — text description of the desired music
- `duration` — length in seconds (max 30)
- `model_size` — `small` (300M), `medium` (1.5B), or `large` (3.3B)

## Usage

```bash
docker build -t musicgen .
docker run --gpus all -p 8001:8001 -v ./models:/app/models musicgen
```

Models are downloaded on first use and cached in `/app/models`.

Requires NVIDIA GPU with CUDA 12.1+ or AMD GPU with ROCm.
