
import re
import spacy


# Load the English NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None


# Technical skills database
SKILLS_DATABASE = [
    "Python",
    "Java",
    "C++",
    "C",
    "JavaScript",
    "TypeScript",
    "SQL",
    "MySQL",
    "MongoDB",
    "PostgreSQL",
    "HTML",
    "CSS",
    "React",
    "Node.js",
    "FastAPI",
    "Django",
    "Flask",
    "Spring Boot",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "NLP",
    "spaCy",
    "TensorFlow",
    "PyTorch",
    "Scikit-learn",
    "Pandas",
    "NumPy",
    "Power BI",
    "Tableau",
    "AWS",
    "Azure",
    "Docker",
    "Git",
    "GitHub",
    "REST API",
    "Data Structures",
    "Algorithms"
]


def extract_email(text):
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    match = re.search(pattern, text)

    return match.group(0) if match else None


def extract_phone(text):
    pattern = r"(?<!\d)(?:\+?\d{1,3}[-.\s]?)?\d{10}(?!\d)"

    match = re.search(pattern, text)

    return match.group(0) if match else None


def extract_name(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # First try NLP-based name recognition
    if nlp:
        doc = nlp(text[:10000])

        for entity in doc.ents:
            if entity.label_ == "PERSON":
                return entity.text.strip()

    # Fallback: inspect the first few lines
    ignored_headings = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "contact"
    }

    for line in lines[:5]:
        if (
            len(line.split()) <= 4
            and not re.search(r"\d|@", line)
            and line.lower() not in ignored_headings
            and re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", line)
        ):
            return line.strip()

    return None


def extract_skills(text):
    found_skills = []

    for skill in SKILLS_DATABASE:
        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )

        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)

    return found_skills


def extract_section_lines(text, keywords):
    lines = text.splitlines()
    results = []

    for line in lines:
        clean_line = line.strip()

        if not clean_line:
            continue

        if any(
            keyword.lower() in clean_line.lower()
            for keyword in keywords
        ):
            results.append(clean_line)

    return results[:10]


def extract_experience_years(text):
    pattern = r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)"

    matches = re.findall(pattern, text, re.IGNORECASE)

    if matches:
        return float(matches[0])

    return None


def parse_resume_text(text):

    if not text or not text.strip():
        return {
            "message": "No readable text found in resume"
        }

    candidate = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),

        "skills": extract_skills(text),

        "education": extract_section_lines(
            text,
            [
                "education",
                "b.tech",
                "bachelor",
                "master",
                "degree",
                "university",
                "college"
            ]
        ),

        "experience": extract_section_lines(
            text,
            [
                "experience",
                "internship",
                "developer",
                "engineer",
                "worked",
                "employment"
            ]
        ),

        "experience_years": extract_experience_years(text)
    }

    return candidate
