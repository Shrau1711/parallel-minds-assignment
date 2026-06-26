from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of given text."""

    prompt = f"""
    Analyze the sentiment of the following text.

    Respond in exactly this format:
    LABEL: <Positive, Negative, or Neutral>
    CONFIDENCE: <a percentage like 87%>
    JUSTIFCATION: <one sentence explaining why>

    Text:
    {text}
    """

    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    raw = response.text.strip()

    result = {"label": "Neutral", "confidence": "0%", "justification": ""}
    
    for line in raw.split("\n"):
        if line.startswith("LABEL:"):
            result["label"] = line.replace("LABEL:", "").strip()
        elif line.startswith("CONFIDENCE:"):
            result["confidence"] = line.replace("CONFIDENCE:", "").strip()
        elif line.startswith("JUSTIFICATION:"):
            result["justification"] = line.replace("JUSTIFICATION:", "").strip()
    
    return result