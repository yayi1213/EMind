"""FastAPI application exposing endpoints for image analysis.

Endpoints:
- POST /analyze : accepts a multipart file upload (image) and returns emotion analysis JSON
- WebSocket /ws : accepts JSON messages with {"frame": "data:image/...;base64,..."} and
  responds with the analysis JSON for each frame. This is useful for real-time UIs.

Security/CORS: CORS is permissive for a local demo. Lock this down in production.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from .processor import analyze_image_b64
import base64
import json
from pathlib import Path
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve a zero-dependency static frontend for quick demos (no Node required).
# This serves the file at project_root/frontend/static_index.html
ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT / 'frontend'
INDEX_HTML = FRONTEND_DIR / 'static_index.html'

if FRONTEND_DIR.exists():
    # mount frontend folder at /static so assets can be loaded as /static/...
    app.mount('/static', StaticFiles(directory=str(FRONTEND_DIR)), name='static')

@app.get('/')
async def serve_root():
    """Serve the static demo index when available. """
    if INDEX_HTML.exists():
        return FileResponse(INDEX_HTML)
    return {"message": "Frontend not available. Start the frontend dev server or create frontend/static_index.html."}


@app.get('/favicon.ico')
async def favicon():
    """Return a tiny inline SVG favicon so browsers don't trigger a 404 on /favicon.ico."""
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
        '<rect width="100%" height="100%" fill="#4f46e5"/>'
        '<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"'
        ' font-size="10" fill="white">ER</text>'
        '</svg>'
    )
    return Response(content=svg, media_type='image/svg+xml')


@app.post('/analyze')
async def analyze_file(file: UploadFile = File(...)):
    """Receive an image file via multipart/form-data and return analysis.

    This endpoint is useful for single-shot analysis (no WebSocket needed).
    The backend decodes the bytes into base64 then calls the analyzer.
    """
    data = await file.read()
    b64 = base64.b64encode(data).decode('utf-8')
    result = analyze_image_b64(b64)
    return result


@app.websocket('/ws')
async def websocket_endpoint(ws: WebSocket):
    """Simple WebSocket endpoint that accepts JSON messages: {"frame": "data:...;base64,..."}.

    For each incoming frame the server runs the analyzer and returns the JSON result.
    This keeps latency low and is suitable for a demo where the frontend pushes periodic frames.
    """
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_text()
            # Expect JSON with {"frame": "data:image/jpeg;base64,..."}
            payload = json.loads(msg)
            frame_b64 = payload.get('frame', '')
            # If the client included a data URL, strip the prefix before analyzing
            if frame_b64.startswith('data:'):
                frame_b64 = frame_b64.split(',', 1)[1]
            result = analyze_image_b64(frame_b64)
            await ws.send_text(json.dumps(result))
    except WebSocketDisconnect:
        print('Client disconnected')
