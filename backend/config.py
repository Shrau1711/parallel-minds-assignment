import os
from dotenv import load_dotenv
from pathlib import Path

# explicitly load .env from the same directory as this file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

INPUT_COST_PER_1K = 0.00015
OUTPUT_COST_PER_1K = 0.0006