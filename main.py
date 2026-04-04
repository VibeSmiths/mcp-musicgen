"""MusicGen FastAPI service — generates instrumental background music from text prompts."""

import io
import os
import struct
import wave
import numpy as np
import torch
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="MusicGen Service")

MODELS_DIR = os.environ.get("MODELS_DIR", "/app/models")
MODEL_CACHE = {}


class GenerateRequest(BaseModel):
    prompt: str
    duration_seconds: float = 10.0
    model: str = "facebook/musicgen-small"


def get_model(model_name: str):
    if model_name not in MODEL_CACHE:
        from audiocraft.models import MusicGen

        model = MusicGen.get_pretrained(model_name, device="cuda" if torch.cuda.is_available() else "cpu")
        MODEL_CACHE[model_name] = model
    return MODEL_CACHE[model_name]


def tensor_to_wav(tensor: torch.Tensor, sample_rate: int) -> bytes:
    """Convert a torch tensor to WAV bytes without torchaudio."""
    audio = tensor.cpu().numpy()
    if audio.ndim == 2:
        audio = audio[0]  # mono
    # Normalize to int16
    audio = np.clip(audio, -1.0, 1.0)
    audio_int16 = (audio * 32767).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())
    return buf.getvalue()


@app.get("/health")
def health():
    return {"status": "ok", "gpu": torch.cuda.is_available()}


@app.get("/models")
def list_models():
    return {
        "models": [
            {"name": "facebook/musicgen-small", "params": "300M", "gpu_required": False},
            {"name": "facebook/musicgen-medium", "params": "1.5B", "gpu_required": True},
            {"name": "facebook/musicgen-large", "params": "3.3B", "gpu_required": True},
        ]
    }


@app.post("/generate")
def generate(req: GenerateRequest):
    try:
        model = get_model(req.model)
        model.set_generation_params(duration=min(req.duration_seconds, 30.0))
        wav = model.generate([req.prompt])

        wav_bytes = tensor_to_wav(wav[0], model.sample_rate)

        return StreamingResponse(
            io.BytesIO(wav_bytes),
            media_type="audio/wav",
            headers={"Content-Disposition": 'attachment; filename="musicgen-output.wav"'},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
