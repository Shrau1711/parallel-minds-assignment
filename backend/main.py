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
    processing_errors = []

    if files:
        for file in files:
            try:
                file_bytes = await file.read()
                filename = file.filename.lower()

                if filename.endswith(".pdf"):
                    extracted_inputs[f"pdf_{file.filename}"] = extract_pdf_text(io.BytesIO(file_bytes))

                elif filename.endswith((".jpg", ".jpeg", ".png", ".webp")):
                    extracted_inputs[f"image_{file.filename}"] = extract_image_text(file_bytes)

                elif filename.endswith((".mp3", ".wav", ".m4a")):
                    extracted_inputs[f"audio_{file.filename}"] = transcribe_audio(file_bytes, file.filename)
                
                else:
                    processing_errors.append(f"Unsupported file type: {file.filename}")

            except Exception as e:
                processing_errors.append(f"Failed to process {file.filename}: {str(e)}")

    if query and not extracted_inputs:
        extracted_inputs["text_query"] = {"text": query}

    try:
        response = run_agent(extracted_inputs, query)
        if processing_errors:
            response["processing_errors"] = processing_errors
        return response
    except Exception as e:
        return {
            "followup": None,
            "trace": [f"[ERROR] Agent crashed: {str(e)}"],
            "result": {"answer": f"Something went wrong on the server: {str(e)}"},
            "extracted": {},
            "cost": {"estimated_tokens": 0, "estimated_cost_usd": 0},
            "processing_errors": processing_errors
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)