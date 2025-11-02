"""Image provider adapters.

This module contains example adapters (stubs). Implement a real provider by adding a function
that calls the provider's API and returns bytes of an image (PNG/JPEG).
"""
from typing import Optional
import os
import base64
import json


def openai_generate_image(prompt: str, api_key: Optional[str] = None, size: str = "512x512") -> bytes:
    """Generate an image using OpenAI Images HTTP API and return raw bytes.

    Requires `api_key` (or `OPENAI_API_KEY` env var). The function requests a single image
    with `response_format: b64_json` and returns decoded bytes for the first image.
    """
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is required for openai_generate_image")

    try:
        import requests
    except Exception:
        raise RuntimeError("`requests` package is required for openai_generate_image")

    url = "https://api.openai.com/v1/images/generations"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "n": 1, "size": size, "response_format": "b64_json"}

    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    resp.raise_for_status()
    data = resp.json()
    try:
        b64 = data["data"][0]["b64_json"]
        return base64.b64decode(b64)
    except Exception:
        raise RuntimeError("Unexpected response from image provider: %r" % data)


def replicate_generate_image(prompt: str, api_key: Optional[str] = None) -> bytes:
    raise NotImplementedError("Replicate provider not implemented in this scaffold.")
