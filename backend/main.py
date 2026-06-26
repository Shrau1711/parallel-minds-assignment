from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
import uvicorn

from processors.pdf_processor import extract_pdf_text
from processors.image_processor import extract_image_text
from processors.audio_processor import transcribe_audio
from agent import run_agent

import io

app = FastAPI(title="Parallel Minds Agent")

# allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("../frontend/index.html")

@app.post("/agent")
async def run_agent_endpoint(
    query: str = Form(""),
    files: Optional[List[UploadFile]] = File(None)
):
    extracted_inputs = {}

    # process each uploaded file based on type
    if files:
        for file in files:
            file_bytes = await file.read()
            filename = file.filename.lower()

            if filename.endswith(".pdf"):
                extracted_inputs[f"pdf_{filename}"] = extract_pdf_text(io.BytesIO(file_bytes))

            elif filename.endswith((".jpg", ".jpeg", ".png", ".webp")):
                extracted_inputs[f"image_{filename}"] = extract_image_text(file_bytes)

            elif filename.endswith((".mp3", ".wav", ".m4a")):
                extracted_inputs[f"audio_{filename}"] = transcribe_audio(file_bytes, file.filename)

    # if only text query, treat it as a text input
    if query and not extracted_inputs:
        extracted_inputs["text_query"] = {"text": query}

    # run the agent
    response = run_agent(extracted_inputs, query)
    return response

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)