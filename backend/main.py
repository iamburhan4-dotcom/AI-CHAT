r"""
AI-CHA Backend – FastAPI server
================================
Handles incoming chat requests and proxies them to an LLM provider.

How to run locally
------------------
1. Create a virtual environment and install dependencies:
       python -m venv .venv
       source .venv/bin/activate        # Windows: .venv\Scripts\activate
       pip install -r requirements.txt

2. Copy the project root .env.example to .env and fill in your API key:
       cp ../.env.example ../.env

3. Start the development server (from the backend/ directory):
       uvicorn main:app --reload --port 8000

4. Open the frontend/index.html in your browser, or visit
       http://127.0.0.1:8000/  (served by FastAPI as a static file)

The single POST endpoint  /api/chat  accepts JSON:
    { "message": "Hello!", "history": [ {"role": "user", "content": "..."}, ... ] }
and returns:
    { "reply": "..." }
"""

import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Load environment variables from the .env file in the project root.
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class Message(BaseModel):
    """A single turn in the conversation."""

    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Payload sent by the frontend."""

    message: str
    history: List[Message] = []


class ChatResponse(BaseModel):
    """Payload returned to the frontend."""

    reply: str


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="AI-CHA", description="AI-powered chat backend", version="0.1.0")

# Allow the frontend to call the API when served from a different origin
# (e.g. opening index.html directly from the file system).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

_frontend_dir = Path(__file__).resolve().parent.parent / "frontend"


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message and return an AI-generated reply.

    Requires OPENAI_API_KEY to be set in the environment (or .env file).
    Falls back to an echo response if no API key is configured, which is
    useful for testing the UI without an actual LLM subscription.
    """
    if not OPENAI_API_KEY:
        # Fallback: echo the message back so the UI can be tested without a key.
        return ChatResponse(reply=f"(echo – no API key configured) {request.message}")

    try:
        # Import here so the server starts even when the openai package is not
        # installed (the echo fallback above will still work).
        from openai import OpenAI  # type: ignore

        client = OpenAI(api_key=OPENAI_API_KEY)

        # Build the message list: system prompt + conversation history + new turn.
        messages = [
            {
                "role": "system",
                "content": (
                    "You are AI-CHA, a helpful and concise conversational assistant."
                ),
            }
        ]
        for turn in request.history:
            messages.append({"role": turn.role, "content": turn.content})
        messages.append({"role": "user", "content": request.message})

        completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
        )
        reply = completion.choices[0].message.content or ""
        return ChatResponse(reply=reply)

    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# Mount the frontend as static files at the root path.
# This is registered AFTER the /api/ routes so those take priority.
# html=True makes StaticFiles serve index.html for directory requests (e.g. "/").
if _frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="frontend")
