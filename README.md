# EMind — CV + LLM Emotion Recognition System

## Team Members
- YaYi Lin (@yayi1213)
- Jasmine Gau (@jasminegau)
- Garrett Smith

## Project Title
EMind — An emotion-recognition system combining computer vision (CV) with an LLM for contextual summarization.

## Short summary (problem & solution)
Problem:
Individuals with ADHD often experience fluctuating attention levels and emotional dysregulation during computer use or study sessions.
However, real-time systems that can recognize these subtle emotional and attentional changes are rare, and developing an AI model that combines visual signals with meaningful feedback requires complex integration of computer vision and language models.

Solution:
EMind offers a lightweight, real-time system that analyzes facial expressions and gaze behavior to infer emotional states and concentration levels in ADHD users.
The backend (FastAPI + DeepFace + OpenCV) detects facial cues such as eye openness, brow tension, and gaze stability, while an integrated LLM generates natural-language summaries and personalized improvement suggestions (e.g., “You seem tired — try a short break or hydration”).
A built-in `DEMO_MODE` allows quick testing without heavy ML dependencies, making EMind both research-ready and accessible for mental-health-focused HCI applications.

## How AI is used
- Computer vision (DeepFace / OpenCV): detect faces and estimate emotion scores (happy, sad, angry, surprised, etc.). The backend analyzer lives in `backend/app/processor.py`.
- LLM (OpenAI or other providers): summarize findings and generate a human-readable message or recommendations from the raw CV output. LLM configuration is in `backend/app/config.py` and the summarizer is in `backend/app/processor.py`.

Notes:
- The repo supports a `DEMO_MODE` that returns synthetic or template outputs so the frontend/demo can be tested without installing heavy ML packages (useful for quick testing or CI).

## Key files (what to focus on)
If the repo isn't fully polished yet, start with these files to understand and extend the system:
- `backend/app/main.py` — FastAPI application, endpoints (`/analyze`, `/ws`) and static demo routing.
- `backend/app/processor.py` — core image decode + emotion analysis + optional LLM summarization.
- `backend/app/config.py` — environment-driven settings for LLM provider and keys.
- `backend/run_analysis_example.py` — small script to test the analyzer locally.
- `frontend/src/App.vue` — main Vue app and UI for sending images/frames to the backend.
- `frontend/static_index.html` & `frontend/static_client.js` — minimal no-Node demo client (served by backend at `/`).

## Quick run (development)
1. Backend: create and activate a Python 3.11 venv, install `requirements.txt`, then run uvicorn (example shown assumes Windows PowerShell and the repo root):

```powershell
# create venv (if needed)
python -m venv .venv311
.\.venv311\Scripts\Activate.ps1
pip install -r backend/requirements.txt
# run backend
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

2. Frontend (optional, requires Node/npm):

```powershell
cd frontend
npm install
npm run dev
```

3. Static demo (no Node): open `http://127.0.0.1:8000/` after backend is running — it serves `frontend/static_index.html` and `static_client.js` for quick demos.

## Notes & next steps
- If you want the full CV pipeline, use Python 3.11 and install `opencv-python-headless`, `tensorflow-cpu`, and `deepface` (these are large; use `DEMO_MODE` to skip them during development).
- To enable LLM summarization, set environment variables in `backend/app/config.py` (e.g., `PROVIDER` and `OPENAI_API_KEY`).
- Consider adding a GitHub Actions workflow to run lightweight tests (or `DEMO_MODE` tests) on push.

If you'd like, I can:
- Run the analysis example inside the created `.venv311` and paste output here.
- Add a short contributor / development checklist to this README.
- Create a simple GitHub Actions workflow that runs `backend/run_analysis_test_fallback.py` in `DEMO_MODE` on PRs.

---
Updated README to give reviewers and contributors a quick orientation. (Files referenced above are in the repository root.)
