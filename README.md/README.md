
# SmartResume — AI Resume Parser & Ranker

SmartResume is an AI-powered resume screening application
designed to extract candidate information from resumes
and help recruiters identify suitable candidates.

## Features

- PDF resume upload
- PDF text extraction
- Candidate information extraction
- Email and phone extraction
- Technical skill identification
- Education and experience extraction
- Structured candidate data validation
- PDF file validation
- Automated unit testing
- Automated API testing

## Technology Stack

### Backend
- Python
- FastAPI
- spaCy
- Pydantic
- PyPDF
- Pytest

### Frontend
- React (planned)

### Database
- MongoDB (planned)

### AI / NLP
- spaCy
- Sentence-BERT (planned)

## Project Structure

SmartResume/
├── Backend/
│   ├── app/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── venv/
├── Frontend/
├── Sample_resumes/
├── docs/
├── .gitignore
└── README.md

## Installation

1. Clone the repository.
2. Open the Backend directory.
3. Create a Python virtual environment.
4. Install dependencies.

```bash
python -m venv venv
```

```bash
pip install -r requirements.txt
```

5. Start the backend.

```bash
python -m uvicorn app.main:app --reload
```

## API Documentation

After starting the backend, visit:

http://127.0.0.1:8000/docs

## Run Automated Tests

```bash
python -m pytest -v
```

## Current Development Status

Backend foundation and initial resume parsing
are implemented.

Semantic resume ranking, database integration,
and frontend development are planned next.

## Future Improvements

- Advanced NLP-based resume parsing
- Sentence-BERT semantic similarity
- Job description matching
- Candidate ranking
- MongoDB integration
- Recruiter dashboard
- OCR support for scanned resumes

## Author

Abhishek Kumar
