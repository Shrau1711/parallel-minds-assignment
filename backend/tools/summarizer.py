from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

def summarize(text: str) -> dict:
    """Summarize text in three formats as required by the assignment."""

    prompt = f"""
    Summarize the following text in exactly three formats:

    1. ONE_LINE: A single sentence summary (max 20 words)
    2. BULLETS: Exactly 3 bullet points highlighting key information
    3. DETAILED: A 5 sentence paragraph summary

    Return your response in this exact format:
    ONE_LINE: <your one line summary>
    BULLETS:
    - <bullet 1>
    - <bullet 2>
    - <bullet 3>
    DETAILED: <your 5 sentence summary>

    Text to summarize:
    {text}
    """

    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    raw = response.text.strip()

    result = {"one_line": "", "bullets": [], "detailed": ""}

    lines = raw.split("\n")
    mode = None
    detailed_lines = []

    for line in lines:
        if line.startswith("ONE_LINE:"):
            result["one_line"] = line.replace("ONE_LINE:", "").strip()
        elif line.startswith("BULLETS:"):
            mode = "bullets"
        elif line.startswith("DETAILED:"):
            mode = "detailed"
            detailed_lines.append(line.replace("DETAILED:", "").strip())
        elif mode == "bullets" and line.strip().startswith("-"):
            result["bullets"].append(line.strip().lstrip("- "))
        elif mode == "detailed" and line.strip():
            detailed_lines.append(line.strip())

    result["detailed"] = " ".join(detailed_lines).strip()
    return result