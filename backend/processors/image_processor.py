import pytesseract
from PIL import Image
import io
from config import TESSERACT_PATH

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def extract_image_text(file_bytes: bytes) -> dict:
    """Extract text from an image using OCR."""
    try:
        image = Image.open(io.BytesIO(file_bytes))

        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        words = [w for w in data["text"] if w.strip()]
        confidences = [c for c, w in zip(data["conf"], data["text"]) if w.strip() and c!= -1]

        full_text = pytesseract.image_to_string(image).strip()

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        confidence_label = "high" if avg_confidence >70 else "medium" if avg_confidence > 40 else "low"

        return {
            "text": full_text,
            "confidence": confidence_label,
            "avg_confidence_score": round(avg_confidence, 2)
        }
    except Exception as e:
        return {"text": "", "confidence": "low", "error": str(e)}
    