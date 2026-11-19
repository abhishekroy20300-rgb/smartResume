from app.services.resume_parser import (
    extract_email,
    extract_phone,
    extract_skills,
    extract_experience_years,
    parse_resume_text,
    calculate_resume_score
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
    
    

# TEST 7: Extract candidate name
def test_extract_candidate_name():

    from app.services.resume_parser import extract_name

    text = """
    Rahul Sharma

    Email: rahul@gmail.com
    Phone: 9876543210

    Skills: Python, Java, SQL
    """

    result = extract_name(text)

    assert result == "Rahul Sharma"


# TEST 8: Ignore headings and job titles
def test_extract_name_skips_headings():

    from app.services.resume_parser import extract_name

    text = """
    Resume
    Software Engineer
    Rahul Sharma

    Email: rahul@gmail.com
    """

    result = extract_name(text)

    assert result == "Rahul Sharma"


# TEST 9: Return None when name is missing
def test_extract_name_returns_none_when_missing():

    from app.services.resume_parser import extract_name

    text = """
    Resume
    Software Engineer
    Python Developer
    Technical Skills
    Python, Java, SQL
    """

    result = extract_name(text)

    assert result is None
    
    
# TEST 10: Extract person entities
def test_extract_person_entity():

    from app.services.resume_parser import extract_entities

    text = "Rahul Sharma is a software developer."

    result = extract_entities(text)

    assert "Rahul Sharma" in result["persons"]


# TEST 11: Extract organization entities
def test_extract_organization_entity():

    from app.services.resume_parser import extract_entities

    text = "Rahul Sharma worked at Tata Consultancy Services."

    result = extract_entities(text)

    assert "Tata Consultancy Services" in result["organizations"]


# TEST 12: Extract location entities
def test_extract_location_entity():

    from app.services.resume_parser import extract_entities

    text = "Rahul Sharma lives in Bangalore."

    result = extract_entities(text)

    assert "Bangalore" in result["locations"]


# TEST 13: Extract date entities
def test_extract_date_entity():

    from app.services.resume_parser import extract_entities

    text = "Rahul worked from January 2024 to December 2025."

    result = extract_entities(text)

    assert any("January 2024" in date for date in result["dates"])


# TEST 14: Integrate entities into complete resume parser
def test_resume_parser_includes_entities():

    from app.services.resume_parser import parse_resume_text

    text = """
    Rahul Sharma
    Worked at Tata Consultancy Services in Bangalore.
    """

    result = parse_resume_text(text)

    assert "entities" in result
    assert "persons" in result["entities"]
    assert "organizations" in result["entities"]
    assert "locations" in result["entities"]
    assert "dates" in result["entities"]



# TEST 15: Extract name from a sentence containing other information
def test_extract_name_from_combined_line():

    from app.services.resume_parser import extract_name

    text = "Rahul Sharma worked at Tata Consultancy Services in Bangalore."

    result = extract_name(text)

    assert result == "Rahul Sharma"

def test_clean_resume_text_normalizes_spaces():
    from app.services.resume_parser import clean_resume_text

    text = "Rahul     Sharma\n\nEmail:    rahul@gmail.com"

    assert clean_resume_text(text) == (
        "Rahul Sharma\nEmail: rahul@gmail.com"
    )


def test_clean_resume_text_removes_null_characters():
    from app.services.resume_parser import clean_resume_text

    text = "Rahul\x00 Sharma"

    assert clean_resume_text(text) == "Rahul Sharma"


def test_clean_resume_text_normalizes_line_endings():
    from app.services.resume_parser import clean_resume_text

    text = "Rahul Sharma\r\n\r\nEmail: rahul@gmail.com"

    assert clean_resume_text(text) == (
        "Rahul Sharma\nEmail: rahul@gmail.com"
    )


def test_clean_resume_text_handles_empty_input():
    from app.services.resume_parser import clean_resume_text

    assert clean_resume_text("") == ""
    assert clean_resume_text(None) == ""
    
    
def test_education_extraction_excludes_professional_summary():

    from app.services.resume_parser import extract_section_lines

    text = """
    PROFESSIONAL SUMMARY
    Python developer with project experience.

    EDUCATION
    Oriental College of Technology, Bhopal
    B.Tech, AIML, 2027

    EXPERIENCE
    Python Developer at ABC Company
    """

    result = extract_section_lines(text, ["education"])

    assert "Oriental College of Technology, Bhopal" in result
    assert "B.Tech, AIML, 2027" in result
    assert "Python developer with project experience." not in result


def test_experience_extraction_excludes_technical_skills():

    from app.services.resume_parser import extract_section_lines

    text = """
    EXPERIENCE
    Python Developer at ABC Company
    Worked on backend development.

    TECHNICAL SKILLS
    Python, Java, SQL
    """

    result = extract_section_lines(text, ["experience"])

    assert "Python Developer at ABC Company" in result
    assert "Worked on backend development." in result
    assert "Python, Java, SQL" not in result


def test_education_extraction_stops_at_next_section():

    from app.services.resume_parser import extract_section_lines

    text = """
    EDUCATION
    Oriental College of Technology
    B.Tech, AIML

    PROJECTS
    SmartResume AI Resume Parser
    """

    result = extract_section_lines(text, ["education"])

    assert "Oriental College of Technology" in result
    assert "B.Tech, AIML" in result
    assert "SmartResume AI Resume Parser" not in result


def test_extract_education_with_academic_background_heading():

    from app.services.resume_parser import extract_section_lines

    text = """
    ACADEMIC BACKGROUND
    Oriental College of Technology, Bhopal
    B.Tech in AIML

    PROJECTS
    SmartResume AI Resume Parser
    """

    result = extract_section_lines(text, ["education"])

    assert "Oriental College of Technology, Bhopal" in result
    assert "B.Tech in AIML" in result
    assert "SmartResume AI Resume Parser" not in result


def test_extract_education_with_qualifications_heading():

    from app.services.resume_parser import extract_section_lines

    text = """
    QUALIFICATIONS
    Bachelor of Technology
    Oriental College of Technology

    SKILLS
    Python, Java, SQL
    """

    result = extract_section_lines(text, ["education"])

    assert "Bachelor of Technology" in result
    assert "Oriental College of Technology" in result
    assert "Python, Java, SQL" not in result


def test_extract_experience_with_employment_history_heading():

    from app.services.resume_parser import extract_section_lines

    text = """
    EMPLOYMENT HISTORY
    Python Developer at ABC Company
    Worked on backend development.

    EDUCATION
    Bachelor of Technology
    """

    result = extract_section_lines(text, ["experience"])

    assert "Python Developer at ABC Company" in result
    assert "Worked on backend development." in result
    assert "Bachelor of Technology" not in result



def test_extract_education_with_same_line_heading():

    from app.services.resume_parser import extract_section_lines

    text = """
    EDUCATION: Oriental College of Technology, Bhopal
    B.Tech in AIML
    PROJECTS
    SmartResume
    """

    result = extract_section_lines(text, ["education"])

    assert "Oriental College of Technology, Bhopal" in result
    assert "B.Tech in AIML" in result
    assert "SmartResume" not in result


def test_extract_experience_with_same_line_heading():

    from app.services.resume_parser import extract_section_lines

    text = """
    EXPERIENCE: Python Developer at ABC Company
    Worked on backend development.
    SKILLS
    Python, Java
    """

    result = extract_section_lines(text, ["experience"])

    assert "Python Developer at ABC Company" in result
    assert "Worked on backend development." in result
    assert "Python, Java" not in result

def test_calculate_resume_score_full_resume():
    candidate = {
        "name": "Rahul Sharma",
        "email": "rahul@gmail.com",
        "phone": "9876543210",
        "skills": ["Python", "Java", "SQL", "React", "MySQL"],
        "education": ["B.Tech"],
        "experience": ["Python Developer"]
    }

    text = "Professional Summary: Python developer"

    result = calculate_resume_score(text, candidate)

    assert result["score"] == 100
    assert result["maximum_score"] == 100
    assert len(result["feedback"]) == 1


def test_calculate_resume_score_missing_contact():
    candidate = {
        "name": "Rahul Sharma",
        "email": None,
        "phone": None,
        "skills": ["Python", "Java", "SQL"],
        "education": ["B.Tech"],
        "experience": ["Python Developer"]
    }

    text = "Professional Summary"

    result = calculate_resume_score(text, candidate)

    assert result["score"] == 75
    assert "Add a valid email address." in result["feedback"]
    assert "Add your contact number." in result["feedback"]


def test_calculate_resume_score_no_skills():
    candidate = {
        "name": "Rahul Sharma",
        "email": "rahul@gmail.com",
        "phone": "9876543210",
        "skills": [],
        "education": ["B.Tech"],
        "experience": ["Python Developer"]
    }

    text = "Professional Summary"

    result = calculate_resume_score(text, candidate)

    assert result["score"] == 80
    assert "Add relevant technical skills." in result["feedback"]


def test_calculate_resume_score_projects_fallback():
    candidate = {
        "name": "Rahul Sharma",
        "email": "rahul@gmail.com",
        "phone": "9876543210",
        "skills": ["Python", "Java", "SQL", "React", "MySQL"],
        "education": ["B.Tech"],
        "experience": []
    }

    text = "Professional Summary\nProjects: SmartResume"

    result = calculate_resume_score(text, candidate)

    assert result["score"] == 95
    assert "Add more details about your work or project experience." in result["feedback"]
    
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