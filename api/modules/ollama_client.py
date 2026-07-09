import json
import httpx
from configs.config import settings


async def generate_json_from_ollama(prompt: str) -> dict:
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.1, "num_ctx": 8192},
            },
        )
    if response.status_code >= 400:
        raise RuntimeError(f"Ollama failed: {response.text}")
    raw = response.json().get("response")
    if not raw:
        raise RuntimeError("Ollama returned no response field.")
    return json.loads(raw)
