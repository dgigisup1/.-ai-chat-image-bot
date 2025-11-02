# .-ai-chat-image-bot

This repository contains a small prototype AI chat assistant scaffold written in Python.

Features
- Chat with a language model (via provider APIs such as OpenAI)
- Ask the assistant to generate code snippets
- Hooks for image and video generation providers (requires external API keys)

What this prototype provides
- A minimal `AIChatBot` class in `src/ai_chatbot.py` with methods: `chat`, `generate_code`, `generate_image`, `generate_video`.
- A simple CLI `src/main.py` to interact locally.
- Tests that validate behavior when API keys are not configured.

Limitations and safety
- This is a scaffold — it does not bundle or run heavy image/video models locally. Image/video generation requires external provider APIs (OpenAI, Replicate, Runway, etc.) and keys.
- The bot cannot genuinely "like" someone; the code can implement a friendly persona, but it should never claim real emotions.

Getting started (quick)
1. Create and activate a Python 3.10+ virtualenv.
2. Install dependencies (if you want to use APIs):

```powershell
python -m pip install -r requirements.txt
```

3. Set environment variables for providers you plan to use, e.g. `OPENAI_API_KEY`.

4. Run the CLI to try:

```powershell
python -m src.main chat --message "Hello!"
python -m src.main code --prompt "Write a Python function to reverse a string"
python -m src.main image --prompt "photorealistic portrait of a person"  # requires provider
python -m src.main video --prompt "10s clip of a beach sunset"          # requires provider
```
Notes: the web UI calls the same backend methods and will require `OPENAI_API_KEY` for image/video features. Video generation (frames + stitching) requires `ffmpeg` on PATH.

Safer defaults and CLI flags
---------------------------

To avoid accidental high-cost requests, the CLI now uses safer defaults:
- Image default size: `512x512` (use `--size` to change).
- Video default duration: `4` seconds and lower fps.

New CLI flags:
- `--size` (image): set image size, e.g. `--size 256x256`.
- `--output` (image/video): set output filename, defaults to `output.png`/`output.mp4`.
- `--yes` (video): skip the confirmation prompt when generating potentially expensive videos.

Example with custom flags:
```powershell
python -m src.main image --prompt "photorealistic cat" --size 256x256 --output cat.png
python -m src.main video --prompt "ocean waves at sunset" --duration 3 --output sunset.mp4 --yes
```

See `src/` for implementation details.

Providers and keys
------------------

- Chat & code: set `OPENAI_API_KEY` for OpenAI chat completions usage.
- Images: the scaffold includes an `openai_generate_image` adapter that uses the OpenAI Images API; it requires `OPENAI_API_KEY`.
- Video: the scaffold can stitch frames into an MP4 using `ffmpeg` and `ffmpeg-python` (the code will call the image provider repeatedly to create frames). You must have the `ffmpeg` binary installed and available on PATH for this to work.

Persona / tone
--------------

You can configure a persona (system prompt) via the `AI_PERSONA` environment variable or pass `--persona` to the CLI chat command. This is a developer-controlled prompt that makes the assistant more friendly or adopt a particular style; it does not confer real emotions.

Security
--------

Never commit your API keys. Use environment variables or a secrets manager. The scaffold prints helpful error messages when keys or required packages are missing.

Web UI
------

A tiny web UI is included under `static/index.html` and a FastAPI app at `src/web.py`.
Run the web UI locally with:

```powershell
python -m pip install -r requirements.txt
uvicorn src.web:app --reload
# then open http://127.0.0.1:8000/
```

Notes: the web UI calls the same backend methods and will require `OPENAI_API_KEY` for image/video features. Video generation (frames + stitching) requires `ffmpeg` on PATH.

Deploying with Docker / PaaS
---------------------------

This project can be run in a container or deployed to PaaS platforms (Render, Heroku, Fly, etc.).

1) Build and run locally with Docker:

```powershell
docker build -t ai-chat-image-bot:latest .
docker run -p 8000:8000 -e OPENAI_API_KEY="sk-..." ai-chat-image-bot:latest
# then open http://127.0.0.1:8000/
```

2) Deploy to Render / Heroku / other PaaS
- Render: create a new Web Service, connect your repo, set the Start Command to `uvicorn src.web:app --host 0.0.0.0 --port 8000` (or leave default) and set environment variables (OPENAI_API_KEY, AI_PERSONA).
- Heroku: use the included `Procfile` and push the repo; set `OPENAI_API_KEY` via the dashboard or `heroku config:set`.

Security and cost notes
- Keep `OPENAI_API_KEY` as a secret in the platform environment settings; never embed it in the image or source.
- Image/video endpoints call external APIs and may incur costs; prefer small sizes and short durations in production.

CI / Continuous deployment
------------------------

This repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` that:
- runs unit tests on push and pull requests to `main`;
- on pushes to `main`, builds a Docker image and publishes it to GitHub Container Registry (GHCR) as `ghcr.io/<owner>/<repo>:latest` and a SHA-tagged image;
- optionally, if you set the secrets `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, and `DOCKERHUB_REPO`, the workflow will also push the built image to Docker Hub.

To enable GHCR publishing no additional secrets are required (the workflow uses `${{ secrets.GITHUB_TOKEN }}` with `packages: write` permission). To publish to Docker Hub, set the three Docker Hub secrets in the repository settings.

If you want a publish-on-PR or alternative tagging strategy, I can update the workflow accordingly.