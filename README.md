# Emotion Recognition System (CV + LLM starter)

This is a full-stack starter project for a real-time emotion recognition system using:

- FastAPI backend (Python) to receive frames and analyze emotions using DeepFace.
- Vue 3 + Vite frontend that captures webcam frames and streams them over WebSocket.
- A simple LLM "placeholder" integration in the backend for enhanced summaries (replace with your LLM of choice).

What is included
- `backend/` - FastAPI app, processor, requirements, Dockerfile
- `frontend/` - Vite + Vue 3 app with webcam capture and WebSocket client
- `README.md` - this file

Quick start (PowerShell)

1) Backend (Python)

# create a venv and install
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# run backend
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

2) Frontend (Node)

# from project root
cd frontend
npm install
npm run dev

Open the frontend dev server shown by vite (usually http://localhost:5173). The frontend connects to the backend WebSocket at ws://localhost:8000/ws by default.

Notes

No-Node quick start (run without installing Node/npm)
-------------------------------------------------
If you don't have Node installed, you can still run a minimal demo using only Python.

1) Start the backend (follow venv + install steps above). Then run:

```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

2) Open your browser to http://localhost:8000/ — the backend will serve a static demo page that captures your webcam and streams frames to the server over WebSocket. This is useful for quick testing without building the Vue app.

When you're ready to use the full Vue 3 frontend, install Node and run the frontend dev server as described earlier.

Security
- This starter is for local development and demos. Add authentication, rate limits, and CORS rules for production.

License
- MIT
