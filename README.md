# AI-CHA

AI-CHA is an interactive, AI-powered conversational assistant designed to handle user queries, automate tasks, and provide intelligent responses.

## Repository structure

```
AI-CHAT/
├── backend/
│   └── main.py          # FastAPI application (chat endpoint + static-file serving)
├── frontend/
│   ├── index.html       # Chat window UI
│   ├── style.css        # Styles
│   └── script.js        # Frontend logic (fetch → /api/chat)
├── requirements.txt     # Python dependencies
├── .env.example         # Placeholder environment variables (copy to .env)
└── README.md
```

## Quick start

### 1 – Clone and set up a virtual environment

```bash
git clone https://github.com/iamburhan4-dotcom/AI-CHAT.git
cd AI-CHAT
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2 – Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3 – Configure your LLM API key

```bash
cp .env.example .env
# Open .env and replace the placeholder with your real OpenAI API key.
```

If you don't have an API key yet the server will still start and echo your
messages back, so you can test the UI without a subscription.

### 4 – Start the backend server

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The server will be available at **http://127.0.0.1:8000**.

### 5 – Open the chat UI

Navigate to **http://127.0.0.1:8000/** in your browser.  
The FastAPI server serves the frontend automatically.

Alternatively you can open `frontend/index.html` directly from the file system
while the backend is running (CORS is enabled for all origins).

## API reference

| Method | Path        | Description                              |
|--------|-------------|------------------------------------------|
| GET    | `/`         | Serves `frontend/index.html`             |
| POST   | `/api/chat` | Accepts `{ message, history }`, returns `{ reply }` |

### Example request

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "history": []}'
```

```json
{ "reply": "Hello! I'm AI-CHA. How can I help you today?" }
```

## Environment variables

| Variable        | Required | Description                              |
|-----------------|----------|------------------------------------------|
| `OPENAI_API_KEY`| Yes*     | OpenAI API key. *Falls back to echo mode if not set. |
| `LLM_MODEL`     | No       | Model name (default: `gpt-4o-mini`)      |

See `.env.example` for a full list with alternative provider keys.

