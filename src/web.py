"""Small FastAPI web UI to interact with the AIChatBot.

Endpoints:
- GET / -> static UI
- POST /api/chat {message, persona?}
- POST /api/code {prompt, lang?}
- POST /api/image {prompt}
- POST /api/video {prompt, duration?}

Run with: `uvicorn src.web:app --reload`
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import base64
from .ai_chatbot import AIChatBot

app = FastAPI(title="AI Chat Image Bot")

# Serve static files from ./static
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except Exception:
        return HTMLResponse("<h1>UI not found</h1><p>Create static/index.html</p>")


@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})


@app.post("/api/chat")
async def api_chat(payload: dict):
    message = payload.get("message")
    persona = payload.get("persona")
    if not message:
        raise HTTPException(status_code=400, detail="message is required")
    bot = AIChatBot(persona=persona)
    try:
        out = bot.chat(message)
        return JSONResponse({"text": out})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/code")
async def api_code(payload: dict):
    prompt = payload.get("prompt")
    lang = payload.get("lang")
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")
    bot = AIChatBot()
    try:
        out = bot.generate_code(prompt, language_hint=lang)
        return JSONResponse({"text": out})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/image")
async def api_image(payload: dict):
    prompt = payload.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")
    bot = AIChatBot()
    try:
        img_bytes = bot.generate_image(prompt)
        b64 = base64.b64encode(img_bytes).decode("ascii")
        return JSONResponse({"data_url": f"data:image/png;base64,{b64}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/video")
async def api_video(payload: dict):
    prompt = payload.get("prompt")
    duration = int(payload.get("duration", 4))
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")
    bot = AIChatBot()
    try:
        vid_bytes = bot.generate_video(prompt, duration_seconds=duration)
        b64 = base64.b64encode(vid_bytes).decode("ascii")
        return JSONResponse({"data_url": f"data:video/mp4;base64,{b64}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
