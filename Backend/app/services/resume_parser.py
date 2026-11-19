
import re
import spacy


# Load the English NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None
    
    
def clean_resume_text(text):
    if not text:
        return ""

    # Remove null characters
    text = text.replace("\x00", "")

    # Standardize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Clean individual lines
    lines = [
        re.sub(r"[ \t]+", " ", line).strip()
        for line in text.splitlines()
    ]

    # Remove unnecessary blank lines
    cleaned_text = "\n".join(
        line for line in lines if line
    )

    return cleaned_text.strip()




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



# Common headings and job titles that should not be treated as names
NON_NAME_TERMS = {
    "resume",
    "curriculum vitae",
    "cv",
    "profile",
    "contact",
    "summary",
    "professional summary",
    "objective",
    "software engineer",
    "software developer",
    "python developer",
    "java developer",
    "web developer",
    "data scientist",
    "data analyst",
    "machine learning engineer",
    "computer science",
    "education",
    "experience",
    "technical skills",
    "projects"
}


def is_valid_name(candidate):

    if not candidate:
        return False

    candidate = re.sub(r"\s+", " ", candidate).strip()
    words = candidate.split()

    if len(words) < 2 or len(words) > 4:
        return False

    if re.search(r"\d|@|https?://|www\.", candidate, re.IGNORECASE):
        return False

    if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", candidate):
        return False

    if candidate.lower().strip(" .") in NON_NAME_TERMS:
        return False

    invalid_words = {
        "engineer", "developer", "analyst", "scientist",
        "manager", "intern", "python", "java",
        "javascript", "machine", "learning", "software",
        "data", "computer", "science", "education",
        "experience", "skills", "projects"
    }

    if any(word.lower().strip(".") in invalid_words for word in words):
        return False

    return True



def extract_name(text):

    if not text or not text.strip():
        return None

    # First attempt: use NLP on the complete resume text
    if nlp:

        doc = nlp(text[:10000])

        for entity in doc.ents:

            if (
                entity.label_ == "PERSON"
                and is_valid_name(entity.text)
            ):
                return entity.text.strip()

    # Second attempt: check the first 8 non-empty lines
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:8]:

        clean_line = line.strip(" |•*-").strip()

        # Remove common contact information after the name
        clean_line = re.split(
            r"\s+(?:email|phone|mobile|contact)\s*:",
            clean_line,
            maxsplit=1,
            flags=re.IGNORECASE
        )[0]

        if is_valid_name(clean_line):
            return clean_line

    return None




def extract_entities(text):

    entities = {
        "persons": [],
        "organizations": [],
        "locations": [],
        "dates": []
    }

    # Check if text and NLP model are available
    if not text or not text.strip() or nlp is None:
        return entities

    # Process resume text using spaCy
    doc = nlp(text[:10000])

    # Extract recognized entities
    for entity in doc.ents:

        value = entity.text.strip()

        if not value:
            continue

        if entity.label_ == "PERSON":
            if value not in entities["persons"]:
                entities["persons"].append(value)

        elif entity.label_ == "ORG":
            if value not in entities["organizations"]:
                entities["organizations"].append(value)

        elif entity.label_ in ("GPE", "LOC"):
            if value not in entities["locations"]:
                entities["locations"].append(value)

        elif entity.label_ == "DATE":
            if value not in entities["dates"]:
                entities["dates"].append(value)

    return entities

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

    heading_aliases = {
        "education": {
            "education",
            "academic background",
            "academic qualifications",
            "qualifications",
            "qualification",
            "education details"
        },
        "experience": {
            "experience",
            "work experience",
            "professional experience",
            "employment history",
            "internships",
            "work history"
        },
                "projects": {
            "projects",
            "personal projects",
            "academic projects",
            "project experience"
        }
    }

    all_headings = {
        heading
        for headings in heading_aliases.values()
        for heading in headings
    }

    all_headings.update({
        "technical skills",
        "skills",
        "projects",
        "personal projects",
        "certifications",
        "achievements",
        "professional summary",
        "summary",
        "objective",
        "contact",
        "contact information",
        "references"
    })

    target_section = None

    for keyword in keywords:
        normalized_keyword = keyword.lower().strip()

        if normalized_keyword in {"education", "experience", "projects"}:
            target_section = normalized_keyword
            break

    if target_section is None:
        return []

    target_headings = heading_aliases[target_section]
    collecting = False

    for line in lines:

        clean_line = line.strip()

        if not clean_line:
            continue

        normalized_line = re.sub(
            r"[^a-zA-Z ]",
            "",
            clean_line
        ).strip().lower()

        # Check for heading and content on the same line
        matched_heading = None

        for heading in sorted(all_headings, key=len, reverse=True):
            if normalized_line.startswith(heading):
                matched_heading = heading
                break

        if matched_heading:

            if matched_heading in target_headings:
                collecting = True

                # Extract content after the heading
                content = re.sub(
                    r"^[^:|\-]*[:|\-]\s*",
                    "",
                    clean_line,
                    count=1
                )

                if content and content != clean_line:
                    results.append(content)

                continue

            if collecting:
                break

            continue

        if collecting:
            results.append(clean_line)

        if len(results) >= 10:
            break

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

    # Clean resume text before extraction
    text = clean_resume_text(text)

    candidate = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "entities": extract_entities(text),

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
        "projects": extract_section_lines(
    text,
    ["projects"]
),

        "experience_years": extract_experience_years(text)
    }

    # Calculate resume quality score
    score_data = calculate_resume_score(text, candidate)
    candidate.update(score_data)

    return candidate


def calculate_resume_score(text, candidate):

    score = 0
    feedback = []

    # 1. Candidate name: 10 points
    if candidate.get("name"):
        score += 10
    else:
        feedback.append("Add your full name.")

    # 2. Email: 10 points
    if candidate.get("email"):
        score += 10
    else:
        feedback.append("Add a valid email address.")

    # 3. Phone: 10 points
    if candidate.get("phone"):
        score += 10
    else:
        feedback.append("Add your contact number.")

    # 4. Professional summary: 15 points
    if re.search(
        r"professional summary|career summary|profile summary|objective",
        text,
        re.IGNORECASE
    ):
        score += 15
    else:
        feedback.append("Consider adding a professional summary.")

    # 5. Technical skills: 20 points
    skills_count = len(candidate.get("skills", []))

    if skills_count >= 5:
        score += 20
    elif skills_count >= 3:
        score += 15
        feedback.append("Add more relevant technical skills.")
    elif skills_count >= 1:
        score += 10
        feedback.append("Expand your technical skills section.")
    else:
        feedback.append("Add relevant technical skills.")

    # 6. Education: 15 points
    if candidate.get("education"):
        score += 15
    else:
        feedback.append("Add your education details.")

    # 7. Experience or projects: 20 points
    if candidate.get("experience"):
        score += 20
    elif re.search(
        r"\bprojects?\b",
        text,
        re.IGNORECASE
    ):
        score += 15
        feedback.append("Add more details about your work or project experience.")
    else:
        feedback.append("Add relevant experience or project details.")

    if not feedback:
        feedback.append("Your resume contains all the checked sections.")

    return {
        "score": score,
        "maximum_score": 100,
        "feedback": feedback
    }


def test_extract_projects_basic():
    text = """
    Rahul Sharma

    EDUCATION
    B.Tech Computer Science

    PROJECTS
    SmartResume
    Vehicle Number Plate Recognition System

    EXPERIENCE
    Python Developer
    """

    result = parse_resume_text(text)

    assert len(result["projects"]) == 2
    assert "SmartResume" in result["projects"]
    assert "Vehicle Number Plate Recognition System" in result["projects"]


def test_extract_projects_does_not_include_experience():
    text = """
    PROJECTS
    SmartResume

    EXPERIENCE
    Python Developer
    """

    result = parse_resume_text(text)

    assert "SmartResume" in result["projects"]
    assert not any(
        "Python Developer" in item
        for item in result["projects"]
    )


def test_resume_without_projects_returns_empty_list():
    text = """
    Rahul Sharma

    EDUCATION
    B.Tech Computer Science

    EXPERIENCE
    Python Developer
    """

    result = parse_resume_text(text)

    assert result["projects"] == []