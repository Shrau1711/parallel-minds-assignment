from google import genai
from config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

def explain_code(code_text: str) -> dict:
    """Explain code, detect bugs and mention time complexity."""
    
    prompt = f"""
    Analyze the following code and respond in exactly this format:
    
    LANGUAGE: <detected programming language>
    EXPLANATION: <clear explanation of what the code does in 3-4 sentences>
    BUGS: <list any bugs or issues, or say 'No bugs detected'>
    TIME_COMPLEXITY: <Big O time complexity with brief explanation>
    
    Code:
    {code_text}
    """
    
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    raw = response.text.strip()
    
    result = {"language": "", "explanation": "", "bugs": "", "time_complexity": ""}
    
    for line in raw.split("\n"):
        if line.startswith("LANGUAGE:"):
            result["language"] = line.replace("LANGUAGE:", "").strip()
        elif line.startswith("EXPLANATION:"):
            result["explanation"] = line.replace("EXPLANATION:", "").strip()
        elif line.startswith("BUGS:"):
            result["bugs"] = line.replace("BUGS:", "").strip()
        elif line.startswith("TIME_COMPLEXITY:"):
            result["time_complexity"] = line.replace("TIME_COMPLEXITY:", "").strip()
    
    return result