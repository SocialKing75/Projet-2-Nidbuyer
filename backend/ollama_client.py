"""Client Ollama local pour les appels LLM du backend."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "180"))


def _ollama_url(path: str) -> str:
    return f"{OLLAMA_BASE_URL}{path}"


def _request_json(method: str, path: str, *, payload: dict | None = None, timeout: int | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        _ollama_url(path),
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout or OLLAMA_TIMEOUT) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Ollama HTTP {exc.code}: {detail}") from exc


def generate_text(
    prompt: str,
    *,
    system: str | None = None,
    history: list[dict] | None = None,
    model: str | None = None,
    temperature: float = 0.2,
    timeout: int | None = None,
) -> str:
    """Genere une reponse texte avec Ollama /api/chat."""
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    for turn in history or []:
        role = turn.get("role")
        content = turn.get("content")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": str(content)})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model or OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    data = _request_json("POST", "/api/chat", payload=payload, timeout=timeout)
    content = (data.get("message") or {}).get("content")
    if not content:
        raise RuntimeError(f"Reponse Ollama vide: {data}")
    return content.strip()


def generate_json(prompt: str, *, model: str | None = None, timeout: int | None = None) -> Any:
    """Genere et parse du JSON avec Ollama."""
    text = generate_text(
        prompt,
        model=model,
        temperature=0,
        timeout=timeout,
        system="Tu retournes uniquement du JSON valide, sans markdown ni texte autour.",
    )
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\]|null)", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(1))


def healthcheck() -> dict:
    """Retourne les modeles Ollama disponibles."""
    data = _request_json("GET", "/api/tags", timeout=10)
    models = [item.get("name") for item in data.get("models", []) if item.get("name")]
    return {
        "base_url": OLLAMA_BASE_URL,
        "default_model": OLLAMA_MODEL,
        "models": models,
    }
