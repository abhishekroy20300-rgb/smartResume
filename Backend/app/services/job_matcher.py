
from sentence_transformers import SentenceTransformer, util


# Load the pretrained semantic similarity model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def calculate_semantic_similarity(resume_text, job_description):
    """
    Calculate semantic similarity between resume and job description.

    Returns a percentage between 0 and 100.
    """

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    if not job_description or not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    embeddings = model.encode(
        [resume_text, job_description],
        convert_to_tensor=True
    )

    similarity = util.cos_sim(
        embeddings[0],
        embeddings[1]
    ).item()

    score = round(max(0, min(1, similarity)) * 100, 2)

    return score
def compare_skills(resume_skills, job_description):

    if not job_description or not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    if not resume_skills:
        resume_skills = []

    from app.services.resume_parser import extract_skills

    required_skills = extract_skills(job_description)

    resume_skills_lower = {
        skill.lower() for skill in resume_skills
    }

    matched_skills = [
        skill for skill in required_skills
        if skill.lower() in resume_skills_lower
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill.lower() not in resume_skills_lower
    ]

    return {
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "total_required_skills": len(required_skills),
        "total_matched_skills": len(matched_skills)
    }
    
    
        

SKILL_RECOMMENDATIONS = {
    
    "python": "Practice Python programming, OOP and problem solving.",
    "java": "Learn Java OOP, Collections and exception handling.",
    "sql": "Practice SQL queries, JOINs, GROUP BY and subqueries.",
    "mysql": "Learn MySQL database design, indexing and transactions.",
    "react": "Learn React components, props, state and hooks.",
    "fastapi": "Build REST APIs using FastAPI and Pydantic.",
    "aws": "Learn AWS cloud fundamentals and deployment.",
    "docker": "Learn Docker images, containers and Docker Compose.",
    "machine learning": "Study supervised learning, model evaluation and feature engineering.",
    "deep learning": "Learn neural networks, CNNs and model training.",
    "nlp": "Study text preprocessing, tokenization and NLP models.",
    "html": "Practice semantic HTML and accessible page structure.",
    "css": "Learn Flexbox, Grid and responsive web design.",
    "javascript": "Practice JavaScript ES6, promises and asynchronous programming.",
    "mongodb": "Learn MongoDB collections, documents and aggregation.",
    "git": "Practice Git branching, commits and collaboration."
}


def generate_learning_recommendations(missing_skills):

    recommendations = []

    for skill in missing_skills:
        recommendation = SKILL_RECOMMENDATIONS.get(
            skill.lower(),
            f"Learn the fundamentals and practical applications of {skill}."
        )

        recommendations.append({
            "skill": skill,
            "recommendation": recommendation
        })

    return recommendations

def analyze_job_match(resume_text, resume_skills, job_description):
    
    

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    if not job_description or not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    semantic_score = calculate_semantic_similarity(
        resume_text,
        job_description
    )

    skill_results = compare_skills(
        resume_skills,
        job_description
    )

    total_required = skill_results["total_required_skills"]

    if total_required > 0:
        skill_score = (
            skill_results["total_matched_skills"]
            / total_required
        ) * 100
    else:
        skill_score = 0

    # Weighted job match score
    final_score = round(
        (semantic_score * 0.4) + (skill_score * 0.6),
        2
    )
    
    learning_recommendations = generate_learning_recommendations(
    skill_results["missing_skills"]
)

def analyze_job_match(resume_text, resume_skills, job_description):

    # Step 1: Validate input
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    if not job_description or not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    # Step 2: Calculate semantic similarity
    semantic_score = calculate_semantic_similarity(
        resume_text,
        job_description
    )

    # Step 3: Compare resume skills with job requirements
    skill_results = compare_skills(
        resume_skills,
        job_description
    )

    # Step 4: Calculate skill score
    total_required = skill_results["total_required_skills"]

    if total_required > 0:
        skill_score = (
            skill_results["total_matched_skills"] / total_required
        ) * 100
    else:
        skill_score = 0

    # Step 5: Calculate final job match score
    final_score = round(
        (semantic_score * 0.4) + (skill_score * 0.6),
        2
    )

    # Step 6: Generate learning recommendations
    learning_recommendations = generate_learning_recommendations(
        skill_results["missing_skills"]
    )

    # Step 7: Return results
    return {
        "match_score": final_score,
        "semantic_score": semantic_score,
        "skill_score": round(skill_score, 2),
        "required_skills": skill_results["required_skills"],
        "matched_skills": skill_results["matched_skills"],
        "missing_skills": skill_results["missing_skills"],
        "learning_recommendations": learning_recommendations
    }
