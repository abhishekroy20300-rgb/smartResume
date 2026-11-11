
from fastapi import FastAPI, UploadFile, File, HTTPException
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from io import BytesIO

from app.services.resume_parser import parse_resume_text
from app.schemas.resume import ResumeData


app = FastAPI(
    title="SmartResume API",
    description="AI Resume Parser and Ranker",
    version="1.0.0"
)

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_PAGES = 50


@app.get("/")
def home():
    return {
        "message": "Welcome to SmartResume!",
        "project": "AI Resume Parser and Ranker",
        "status": "Running Successfully"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):

    # 1. Validate filename and extension
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    # 2. Read uploaded file
    try:
        file_bytes = await file.read()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to read uploaded file"
        )

    # 3. Check empty file
    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    # 4. Check file size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must be below 10 MB"
        )

    # 5. Read and validate PDF
    try:
        pdf = PdfReader(BytesIO(file_bytes), strict=False)

        # Check password protection
        if pdf.is_encrypted:
            try:
                if pdf.decrypt("") == 0:
                    raise HTTPException(
                        status_code=422,
                        detail="Password-protected PDFs are not supported"
                    )
            except HTTPException:
                raise
            except Exception:
                raise HTTPException(
                    status_code=422,
                    detail="Unable to decrypt PDF"
                )

        total_pages = len(pdf.pages)

        # Check page count
        if total_pages == 0:
            raise HTTPException(
                status_code=422,
                detail="PDF contains no pages"
            )

        if total_pages > MAX_PAGES:
            raise HTTPException(
                status_code=413,
                detail="PDF cannot contain more than 50 pages"
            )

        # 6. Extract text
        extracted_text = ""

        for page in pdf.pages:
            extracted_text += (page.extract_text() or "") + "\n"

    except HTTPException:
        raise

    except (PdfReadError, ValueError, OSError):
        raise HTTPException(
            status_code=422,
            detail="Invalid or corrupted PDF file"
        )

    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Unable to process this PDF file"
        )

    # 7. Check extracted text
    if not extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable text found. Scanned PDFs require OCR."
        )

    # 8. Parse resume
    try:
        candidate_data = parse_resume_text(extracted_text)

        validated_candidate = ResumeData.model_validate(
            candidate_data
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Resume processing failed"
        )

    # 9. Return structured response
    return {
        "filename": file.filename,
        "total_pages": total_pages,
        "extracted_text": extracted_text,
        "candidate_information": validated_candidate.model_dump(),
        "message": "Resume uploaded and parsed successfully"
    }
