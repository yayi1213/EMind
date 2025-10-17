"""Image analysis and (optional) LLM enrichment utilities.

This module provides:
- _b64_to_cv2: helper to decode a base64 data URL or raw base64 into an OpenCV BGR numpy array
- analyze_image_b64: runs DeepFace emotion analysis on a single image and returns a small JSON
- llm_summarize: optional LLM-based enrichment; configurable via `backend/app/config.py`

Notes on LLM integration:
- By default the project uses a simple template summary (fast, no network).
- If you set PROVIDER=openai and provide OPENAI_API_KEY in the environment, the code will
  attempt to call OpenAI to produce a concise human-friendly summary.

Keep LLM calls minimal to avoid heavy costs in demos; for production add rate-limiting,
batching, retries and safe content handling.
"""

"""Image analysis and (optional) LLM enrichment utilities.

This module intentionally keeps heavy CV dependencies optional so the server
can run in a lightweight demo environment. If OpenCV/NumPy/Pillow/DeepFace
are installed, real analysis will run; otherwise the analyzer returns a
safe demo response.
"""

import os
import base64
from io import BytesIO
from typing import Dict, Any

# Optional imports: these may be missing in light-weight environments
try:
    import cv2
except Exception:
    cv2 = None

try:
    import numpy as np
except Exception:
    np = None

try:
    from PIL import Image
except Exception:
    Image = None

try:
    from deepface import DeepFace
except Exception:
    DeepFace = None

from . import config

# If DEMO_MODE is set (1/true/yes) the processor will skip any CV/DeepFace work
# and return a safe demo response. This is useful for machines without heavy
# CV dependencies during development/testing.
DEMO_MODE = str(os.environ.get('DEMO_MODE', '')).lower() in ('1', 'true', 'yes')


def _b64_to_cv2(b64str: str):
    """Decode a base64 (or data URL) image and return an OpenCV BGR numpy array.

    Returns None when image decoding or numpy is not available so callers
    can fall back to demo behavior instead of crashing.
    """
    if b64str.startswith('data:'):
        b64str = b64str.split(',', 1)[1]
    b = base64.b64decode(b64str)
    if Image is None:
        return None
    img = Image.open(BytesIO(b)).convert('RGB')
    if np is None:
        return None
    return np.array(img)[:, :, ::-1]


def analyze_image_b64(b64str: str) -> Dict[str, Any]:
    """Analyze a base64 image and return emotion info.

    Provides a safe fallback when heavy CV libs are unavailable.
    """
    try:
        img = _b64_to_cv2(b64str)
    except Exception as e:
        return {"error": "invalid_image", "detail": str(e)}

    # If DEMO_MODE is enabled, or we couldn't decode the image / numpy isn't installed,
    # return a demo response rather than attempting heavy CV work.
    if DEMO_MODE or img is None:
        emotion = 'unknown'
        emotions = {}
        summary = llm_summarize(emotion, emotions)
        return {'emotion': emotion, 'emotions': emotions, 'summary': summary}

    emotion = 'unknown'
    emotions = {}

    # Run DeepFace if available and the CV stack exists
    if DeepFace is not None and cv2 is not None and np is not None:
        try:
            analysis = DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
            if isinstance(analysis, list):
                analysis = analysis[0]
            emotion = analysis.get('dominant_emotion', 'unknown')
            emotions = analysis.get('emotion', {}) or {}
        except Exception:
            emotion = 'unknown'
            emotions = {}

    summary = llm_summarize(emotion, emotions)
    return {'emotion': emotion, 'emotions': emotions, 'summary': summary}


def llm_summarize(emotion: str, emotions: Dict[str, float]) -> str:
    """Return a concise summary; optionally call an LLM provider configured in `config`.

    Falls back to a small local template when an external provider isn't configured
    or when network/packages are missing.
    """
    provider = getattr(config, 'PROVIDER', '')

    def _template():
        top = emotion or 'unknown'
        val = emotions.get(top, None)
        if val is not None:
            try:
                return f"Detected {top} with confidence {float(val):.1f}%"
            except Exception:
                return f"Detected {top} (confidence unavailable)"
        return f"Detected {top}"

    if provider == 'openai':
        try:
            import openai
            api_key = getattr(config, 'OPENAI_API_KEY', '')
            if not api_key:
                return _template()
            openai.api_key = api_key
            prompt = (
                f"You are an assistant that summarizes facial emotion analysis. The detected dominant emotion is '{emotion}'. "
                f"Detailed scores: {emotions}. Return a concise 1-2 sentence friendly summary."
            )
            model = getattr(config, 'OPENAI_MODEL', 'gpt-3.5-turbo')
            try:
                resp = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=60,
                    temperature=0.2,
                )
                return resp['choices'][0]['message']['content'].strip()
            except Exception:
                try:
                    resp = openai.Completion.create(model=model, prompt=prompt, max_tokens=60, temperature=0.2)
                    return resp['choices'][0]['text'].strip()
                except Exception:
                    return _template()
        except Exception:
            return _template()

    return _template()
