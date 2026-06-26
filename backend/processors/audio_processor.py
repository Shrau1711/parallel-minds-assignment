import tempfile
import os
from config import GEMINI_API_KEY, GEMINI_MODEL
from google import genai
from google.genai import types

client = genai.Client(api_key=GEMINI_API_KEY)

def transcribe_audio(file_bytes: bytes, filename: str) -> dict:
    """Transcribe audio using Gemini's native audio understanding."""
    try:
        suffix = os.path.splitext(filename)[-1].lower() or ".mp3"
        
        mime_map = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav", 
            ".m4a": "audio/mp4"
        }
        mime = mime_map.get(suffix, "audio/mpeg")

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                types.Part.from_bytes(data=file_bytes, mime_type=mime),
                "Transcribe this audio file completely and accurately. Return only the transcript text, nothing else."
            ]
        )

        text = response.text.strip() if response.text else ""
        
        return {
            "text": text,
            "language": "auto-detected",
            "duration": "unknown",
            "confidence": "high" if text else "low"
        }

    except Exception as e:
        return {
            "text": f"Audio transcription failed: {str(e)}",
            "language": "unknown", 
            "duration": "unknown",
            "confidence": "low",
            "error": str(e)
        }