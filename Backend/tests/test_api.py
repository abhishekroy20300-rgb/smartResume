
from io import BytesIO

from fastapi.testclient import TestClient
from pypdf import PdfWriter
from docx import Document
from reportlab.pdfgen import canvas


# TEST 8: Successfully upload DOCX resume
def test_upload_valid_docx():

    docx_data = create_valid_docx()

    response = client.post(
        "/upload-resume",
        files={
            "file": (
                "resume.docx",
                docx_data,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        }
    )

    assert response.status_code == 200

    result = response.json()

    assert result["filename"] == "resume.docx"
    assert result["file_type"] == "docx"
    assert result["message"] == "Resume uploaded and parsed successfully"

    candidate = result["candidate_information"]

    assert candidate["email"] == "rahul@gmail.com"
    assert candidate["phone"] == "9876543210"


# TEST 9: Reject corrupted DOCX
def test_upload_rejects_corrupted_docx():

    response = client.post(
        "/upload-resume",
        files={
            "file": (
                "corrupted.docx",
                b"This is not a valid DOCX document",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        }
    )

    assert response.status_code == 422

from app.main import app


# Create a test client
client = TestClient(app)


# Helper function to create a valid blank PDF
def create_blank_pdf():

    pdf_buffer = BytesIO()

    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    writer.write(pdf_buffer)

    return pdf_buffer.getvalue()

# Helper function to create a valid DOCX
def create_valid_docx():

    doc_buffer = BytesIO()

    document = Document()

    document.add_paragraph("Rahul Sharma")
    document.add_paragraph("Email: rahul@gmail.com")
    document.add_paragraph("Phone: 9876543210")
    document.add_paragraph("Skills: Python, Java, SQL")

    document.save(doc_buffer)

    return doc_buffer.getvalue()

# Helper function to create a valid PDF resume
def create_valid_pdf():

    pdf_buffer = BytesIO()

    pdf = canvas.Canvas(pdf_buffer)

    pdf.drawString(100, 750, "Rahul Sharma")
    pdf.drawString(100, 720, "Email: rahul@gmail.com")
    pdf.drawString(100, 690, "Phone: 9876543210")
    pdf.drawString(100, 660, "Skills: Python, Java, SQL")

    pdf.save()

    return pdf_buffer.getvalue()


# TEST 1: Home endpoint
def test_home_endpoint():

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "Running Successfully"


# TEST 2: Health endpoint
def test_health_endpoint():

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# TEST 3: Reject non-PDF file
def test_upload_rejects_non_pdf():

    response = client.post(
        "/upload-resume",
        files={
            "file": (
                "resume.txt",
                b"This is a text file",
                "text/plain"
            )
        }
    )

    assert response.status_code == 400


# TEST 4: Reject empty file
def test_upload_rejects_empty_file():

    response = client.post(
        "/upload-resume",
        files={
            "file": (
                "empty.pdf",
                b"",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 400


# TEST 5: Reject corrupted PDF
def test_upload_rejects_corrupted_pdf():

    response = client.post(
        "/upload-resume",
        files={
            "file": (
                "corrupted.pdf",
                b"This is not a valid PDF document",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 422


# TEST 6: Reject PDF without readable text
def test_upload_rejects_blank_pdf():

    pdf_data = create_blank_pdf()

    response = client.post(
        "/upload-resume",
        files={
            "file": (
                "blank.pdf",
                pdf_data,
                "application/pdf"
            )
        }
    )

    assert response.status_code == 422


# TEST 7: Reject files larger than 10 MB
def test_upload_rejects_large_file():

    large_file = b"x" * (10 * 1024 * 1024 + 1)

    response = client.post(
        "/upload-resume",
        files={
            "file": (
                "large.pdf",
                large_file,
                "application/pdf"
            )
        }
    )

    assert response.status_code == 413

# TEST 8: Successfully upload DOCX resume
def test_upload_valid_docx():

    docx_data = create_valid_docx()

    response = client.post(
        "/upload-resume",
        files={
            "file": (
                "resume.docx",
                docx_data,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        }
    )

    assert response.status_code == 200

    result = response.json()

    assert result["filename"] == "resume.docx"
    assert result["file_type"] == "docx"
    assert result["message"] == "Resume uploaded and parsed successfully"

    candidate = result["candidate_information"]

    assert candidate["email"] == "rahul@gmail.com"
    assert candidate["phone"] == "9876543210"


# TEST 9: Reject corrupted DOCX
def test_upload_rejects_corrupted_docx():

    response = client.post(
        "/upload-resume",
        files={
            "file": (
                "corrupted.docx",
                b"This is not a valid DOCX document",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        }
    )

    assert response.status_code == 422
    
    # TEST 10: Successfully upload PDF resume
def test_upload_valid_pdf():

    pdf_data = create_valid_pdf()

    response = client.post(
        "/upload-resume",
        files={
            "file": (
                "resume.pdf",
                pdf_data,
                "application/pdf"
            )
        }
    )

    assert response.status_code == 200

    result = response.json()

    assert result["filename"] == "resume.pdf"
    assert result["file_type"] == "pdf"
    assert result["total_pages"] == 1

    candidate = result["candidate_information"]

    assert candidate["name"] == "Rahul Sharma"
    assert candidate["email"] == "rahul@gmail.com"
    assert candidate["phone"] == "9876543210"