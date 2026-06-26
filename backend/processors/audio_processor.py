import tempfile
import os
from config import GEMINI_API_KEY, GEMINI_MODEL
from google import genai
from google.genai import types

client = genai.Client(api_key=GEMINI_API_KEY)

def transcribe_audio(file_bytes: bytes, filename: str) -> dict:
    """Transcribe audio using Gemini's native audio understanding."""
    try:
        suffix = os.path.splitext(filename)[-1] or ".mp3"
        mime = "audio/mpeg" if suffix in [".mp3"] else "audio/wav"

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=file_bytes, mime_type=mime),
                "Transcribe this audio file completely and accurately. Return only the transcript text, nothing else."
            ]
        )

        return {
            "text": response.text.strip(),
            "language": "auto-detected",
            "duration": "unknown"
        }

    except Exception as e:
        return {"text": "", "language": "unknown", "duration": "unknown", "error": str(e)}