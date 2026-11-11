
from io import BytesIO

from fastapi.testclient import TestClient
from pypdf import PdfWriter

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
