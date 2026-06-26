import whisper
import tempfile
import os

model = whisper.load_model("small")

def transcribe_audio(file_bytes: bytes, filename: str) -> dict:
    """Transcribe audio file to text using OpenAI Whisper locally."""
    try:

        suffix = os.path.splitext(filename)[-1] or ".mp3"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        result = model.transcribe(tmp_path)
        os.unlink(tmp_path)

        duration_seconds = result.get("duration", 0)
        minutes = int(duration_seconds // 60)
        seconds = int(duration_seconds % 60)

        return {
            "text": result["text"].strip(),
            "language": result.get("language", "unknown"),
            "duration": f"{minutes}m {seconds}s"
        }
    except Exception as e:
        return {"text": "", "language": "unknown", "duration": "0m 0s", "error": str(e)}