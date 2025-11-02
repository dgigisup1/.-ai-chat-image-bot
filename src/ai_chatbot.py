import os
import json
from typing import List, Optional


class AIChatBot:
    """Minimal AI chatbot scaffold.

    - Uses environment variables for API keys (e.g., OPENAI_API_KEY)
    - Provides methods that call external providers when configured.
    - If no key/provider is configured, methods raise informative errors.
    - Supports a configurable persona/system prompt via `persona` or env `AI_PERSONA`.
    """

    def __init__(self, openai_api_key: Optional[str] = None, persona: Optional[str] = None):
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        # Persona/system prompt used for chat completions when set.
        # If not provided, the model is neutral/helpful by default.
        self.persona = persona or os.getenv("AI_PERSONA")

    def _require_openai(self):
        if not self.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY not set. Set the OPENAI_API_KEY env var to use this feature."
            )

    def chat(self, message: str, system: Optional[str] = None) -> str:
        """Send a message to a chat completions endpoint (OpenAI compatible).

        Returns the assistant text. This implementation calls the OpenAI ChatCompletions HTTP API
        if `OPENAI_API_KEY` is set. It's a minimal wrapper and can be adapted to other providers.
        """
        self._require_openai()

        # Import requests here so running tests that don't need network won't require the package.
        try:
            import requests
        except Exception:
            raise RuntimeError("`requests` package is required to call the chat provider. Install it or ensure it's available.")

        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"}
        messages = []
        # Priority: explicit system param > configured persona > none
        system_prompt = system or self.persona
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        payload = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "max_tokens": 800,
        }

        resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Minimal defensive parsing
        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            raise RuntimeError("Unexpected response from chat provider: %r" % data)

    def generate_code(self, prompt: str, language_hint: Optional[str] = None) -> str:
        """Ask the model to generate code. Returns a text response (code included).

        This uses the `chat` method with a code-focused system prompt.
        """
        system = "You are a helpful programming assistant. Provide code in a single block with minimal explanations unless requested."
        if language_hint:
            system += f" Target language: {language_hint}."
        return self.chat(prompt, system=system)

    def generate_image(self, prompt: str, size: str = "512x512") -> bytes:
        """Generate an image using a configured provider.

        Current implementation will try to use OpenAI Images if `OPENAI_API_KEY` is set.
        Returns raw image bytes (PNG/JPEG). Raises RuntimeError when no provider/key is available.
        """
        # Prefer explicit OPENAI_API_KEY; fallback to env var already stored
        api_key = self.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "No image provider configured. Set OPENAI_API_KEY to enable image generation."
            )

        # Lazy import of provider to avoid hard dependency in tests
        try:
            from .image_provider import openai_generate_image
        except Exception:
            raise RuntimeError("Image provider adapter not available in package.")

        return openai_generate_image(prompt, api_key=api_key, size=size)

    def generate_video(self, prompt: str, duration_seconds: int = 4) -> bytes:
        """Generate a short video by producing frames (via image provider) and combining with ffmpeg.

        This helper will:
        - require `OPENAI_API_KEY` for image frames (unless you replace the provider)
        - require `ffmpeg` binary and `ffmpeg-python` package to stitch frames

        For now this implementation produces `fps * duration_seconds` frames by calling the
        configured image provider with slight frame prompts and then stitches them into MP4 bytes.
        """
        api_key = self.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("No image provider configured. Set OPENAI_API_KEY to enable video generation.")

        try:
            from .image_provider import openai_generate_image
            from .video_provider import frames_to_mp4_bytes
            from PIL import Image
            import base64
            import io
        except Exception:
            raise RuntimeError("Video generation requires provider adapters and Pillow/ffmpeg-python installed.")

        # Safer defaults: lower fps to reduce number of image API calls and cost
        fps = 6
        total_frames = max(1, int(fps * duration_seconds))
        frames = []
        for i in range(total_frames):
            frame_prompt = f"{prompt} -- frame {i+1} of {total_frames} -- cinematic"
            img_bytes = openai_generate_image(frame_prompt, api_key=api_key)
            frames.append(img_bytes)

        return frames_to_mp4_bytes(frames, fps=fps)


__all__ = ["AIChatBot"]
