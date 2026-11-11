
from app.services.resume_parser import (
    extract_email,
    extract_phone,
    extract_skills,
    extract_experience_years,
    parse_resume_text
)


def test_extract_email():
    text = "Contact me at rahul@gmail.com"
    result = extract_email(text)

    assert result == "rahul@gmail.com"


def test_extract_phone():
    text = "Phone: 9876543210"
    result = extract_phone(text)

    assert result == "9876543210"


def test_extract_skills():
    text = "I know Python, Java and SQL"
    result = extract_skills(text)

    assert "Python" in result
    assert "Java" in result
    assert "SQL" in result


def test_extract_experience_years():
    text = "I have 2 years of experience"
    result = extract_experience_years(text)

    assert result == 2.0


def test_empty_resume():
    result = parse_resume_text("")

    assert result == {
        "message": "No readable text found in resume"
    }


def test_parse_resume_text():
    text = """
    Rahul Sharma
    Email: rahul@gmail.com
    Phone: 9876543210

    Skills: Python, Java, SQL

    Education: B.Tech Computer Science

    Experience: 2 years
    """

    result = parse_resume_text(text)

    assert result["email"] == "rahul@gmail.com"
    assert result["phone"] == "9876543210"
    assert "Python" in result["skills"]
    assert "Java" in result["skills"]
    assert result["experience_years"] == 2.0
