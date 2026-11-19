from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User

from app.auth.security import hash_password, verify_password
from app.auth.token import create_access_token

from app.schemas.auth import (
    UserRegister,
    UserResponse,
    UserLogin,
    TokenResponse
)
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from io import BytesIO

from docx import Document
from pydantic import BaseModel

from app.services.job_matcher import analyze_job_match
from app.services.resume_parser import parse_resume_text
from app.schemas.resume import ResumeData

import json

from app.database.models import User, ResumeAnalysis
from app.auth.dependencies import get_current_user


app = FastAPI(
    title="SmartResume API",
    description="AI Resume Parser and Ranker",
    version="1.0.0"
)

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_PAGES = 50
class JobMatchRequest(BaseModel):
    resume_text: str
    resume_skills: list[str]
    job_description: str

def extract_docx_text(file_bytes):
    doc = Document(BytesIO(file_bytes))

    extracted_parts = []

    # Extract normal paragraphs
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            extracted_parts.append(paragraph.text)

    # Extract text from tables
    for table in doc.tables:
        for row in table.rows:
            cells = [
                cell.text.strip()
                for cell in row.cells
                if cell.text.strip()
            ]

            if cells:
                extracted_parts.append(" | ".join(cells))

    return "\n".join(extracted_parts)

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

    # 1. Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    filename = file.filename.lower()

    # 2. Validate extension
    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported"
        )

    # 3. Read uploaded file
    try:
        file_bytes = await file.read()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to read uploaded file"
        )

    # 4. Validate file size
    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must be below 10 MB"
        )

    # 5. Extract text based on file type
    extracted_text = ""
    total_pages = None

    if filename.endswith(".pdf"):

        try:
            pdf = PdfReader(BytesIO(file_bytes), strict=False)

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

            for page in pdf.pages:
                extracted_text += (page.extract_text() or "") + "\n"

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=422,
                detail="Invalid or corrupted PDF file"
            )

    elif filename.endswith(".docx"):

        try:
            extracted_text = extract_docx_text(file_bytes)

        except Exception:
            raise HTTPException(
                status_code=422,
                detail="Invalid or corrupted DOCX file"
            )

    # 6. Check extracted text
    if not extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable text found in resume"
        )

    # 7. Parse resume
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

    # 8. Return response
    return {
        "filename": file.filename,
        "file_type": filename.rsplit(".", 1)[-1],
        "total_pages": total_pages,
        "extracted_text": extracted_text,
        "candidate_information": validated_candidate.model_dump(),
        "message": "Resume uploaded and parsed successfully"
    }

@app.post("/match-job")
def match_job(request: JobMatchRequest):

    try:
        result = analyze_job_match(
            request.resume_text,
            request.resume_skills,
            request.job_description
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
        
        
@app.post("/register", response_model=UserResponse, status_code=201)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    # Check whether email already exists
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered"
        )

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create new user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="User registration failed"
        )

    return new_user


@app.post("/login", response_model=TokenResponse)
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    # Find user by email
    user = db.query(User).filter(
        User.email == login_data.email
    ).first()

    # Verify email and password
    if not user or not verify_password(
        login_data.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Generate JWT access token
    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/upload-resume-authenticated")
async def upload_resume_authenticated(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Read and validate the uploaded file
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )

    filename = file.filename.lower()

    if not (filename.endswith(".pdf") or filename.endswith(".docx")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported"
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must be below 10 MB"
        )

    # Extract resume text
    total_pages = None

    try:
        if filename.endswith(".pdf"):
            pdf = PdfReader(BytesIO(file_bytes), strict=False)

            if pdf.is_encrypted:
                if pdf.decrypt("") == 0:
                    raise HTTPException(
                        status_code=422,
                        detail="Password-protected PDFs are not supported"
                    )

            total_pages = len(pdf.pages)

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

            extracted_text = "\n".join(
                page.extract_text() or ""
                for page in pdf.pages
            )

        else:
            extracted_text = extract_docx_text(file_bytes)

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Invalid or corrupted resume file"
        )

    if not extracted_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No readable text found in resume"
        )

    # Parse resume
    try:
        candidate_data = parse_resume_text(extracted_text)
        validated_candidate = ResumeData.model_validate(candidate_data)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Resume processing failed"
        )

    candidate_result = validated_candidate.model_dump()

    # Save analysis for the logged-in user
    analysis = ResumeAnalysis(
        user_id=current_user.id,
        filename=file.filename,
        resume_score=candidate_result.get("score", 0),
        extracted_text=extracted_text,
        analysis_data=json.dumps(candidate_result)
    )

    try:
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to save resume analysis"
        )

    return {
        "analysis_id": analysis.id,
        "filename": file.filename,
        "candidate_information": candidate_result,
        "message": "Resume uploaded and analysis saved successfully"
    }

@app.get("/analysis-history")
def get_analysis_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    analyses = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.user_id == current_user.id
    ).order_by(
        ResumeAnalysis.created_at.desc()
    ).all()

    return {
        "total_analyses": len(analyses),
        "history": [
            {
                "id": analysis.id,
                "filename": analysis.filename,
                "resume_score": analysis.resume_score,
                "created_at": analysis.created_at,
                "candidate_information": json.loads(
                    analysis.analysis_data
                ) if analysis.analysis_data else {}
            }
            for analysis in analyses
        ]
    }
