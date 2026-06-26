import pdfplumber

def extract_pdf_text(file_bytes: bytes) -> dict:
    """Extract text from a PDF given it's raw bytes."""
    extracted_pages = []

    with pdfplumber.open(file_bytes) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_pages.append(f"[Page {i+1}]\n{page_text}")

    if not extracted_pages:
        return {"text": "", "confidence": "low", "pages": "0"}
    
    full_text = "\n\n".join(extracted_pages)
    return {
        "text": full_text,
        "confidence": "high",
        "pages": len(extracted_pages)
    }