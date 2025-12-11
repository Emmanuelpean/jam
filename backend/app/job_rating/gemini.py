"""Use Gemini LLM to rate how well scraped jobs match user qualifications."""

import json

from google import genai

from app.config import settings

__version__ = 1

client = genai.Client(api_key=settings.gemini_api_key)


def ai_score_job(
    user_experience: str | None,
    user_education: str | None,
    user_skills: str | None,
    user_qualities: str | None,
    user_interests: str | None,
    job_title: str | None,
    job_company: str | None,
    job_description: str | None,
) -> dict:
    """Use Gemini LLM to score how well a user's qualifications match a scraped job.
    :param user_experience: User's experience description
    :param user_education: User's education description
    :param user_skills: User's skills description
    :param user_qualities: User's qualities description
    :param user_interests: User's interests description
    :param job_title: Job title
    :param job_company: Job company
    :param job_description: Job description
    :return: JSON string with overall score and explanation."""

    # Build candidate profile section dynamically
    candidate_sections = []
    if user_experience:
        candidate_sections.append(f"- **Experience**: {user_experience}")
    else:
        candidate_sections.append("- **Experience**: Not provided")

    if user_education:
        candidate_sections.append(f"- **Education**: {user_education}")
    else:
        candidate_sections.append("- **Education**: Not provided")

    if user_skills:
        candidate_sections.append(f"- **Skills**: {user_skills}")
    else:
        candidate_sections.append("- **Skills**: Not provided")

    if user_qualities:
        candidate_sections.append(f"- **Qualities**: {user_qualities}")
    else:
        candidate_sections.append("- **Qualities**: Not provided")

    if user_interests:
        candidate_sections.append(f"- **Interests**: {user_interests}")
    else:
        candidate_sections.append("- **Interests**: Not provided")

    candidate_profile = "\n".join(candidate_sections)

    # Build job details section dynamically
    job_sections = []
    if job_title:
        job_sections.append(f"- **Title**: {job_title}")
    if job_company:
        job_sections.append(f"- **Company**: {job_company}")
    if job_description:
        job_sections.append(f"- **Description**: {job_description}")

    job_details = "\n".join(job_sections) if job_sections else "- **No job information provided**"

    llm_prompt = f"""
    You are an expert career matching agent specializing in evaluating candidate-job compatibility. Your task is to analyze how well a candidate matches a specific job opportunity across multiple dimensions.
    
    ## Input Information
    
    ### Candidate Profile
    {candidate_profile}
    
    ### Job Details
    {job_details}
    
    ## Evaluation Framework
    
    Assess the candidate across these dimensions and provide a score (0-10) for each dimension **WHERE DATA IS AVAILABLE**:
    
    1. **Technical Fit** (0-10): Match between candidate's technical skills and job requirements
       - Set to `null` if Skills are "Not provided"
       
    2. **Experience Alignment** (0-10): Relevance of past roles to the position's responsibilities
       - Set to `null` if Experience is "Not provided"
       
    3. **Educational Match** (0-10): Degree requirements and academic background alignment
       - Set to `null` if Education is "Not provided"
       
    4. **Interest Match** (0-10): Alignment of candidate's interests with job role and company culture
       - Set to `null` if Interests are "Not provided"
    
    5. **Overall Score** (0-10): Holistic assessment of candidate-job fit
       - Calculate based ONLY on the dimensions that have scores (exclude null values from average)
       - If ALL dimensions are null, set overall_score to `null` as well
    
    ## Output Format
    
    Return your assessment as valid JSON with this exact structure (ALL fields must be present):
    
    {{
        "overall_score": <integer 0-10 or null>,
        "technical_fit": <integer 0-10 or null>,
        "experience_alignment": <integer 0-10 or null>,
        "educational_match": <integer 0-10 or null>,
        "interest_match": <integer 0-10 or null>,
        "explanation": "<2-3 sentences explaining your recommendation, noting any missing information that limited the assessment>"
    }}
    
    ## Evaluation Guidelines
    
    - **Return null (not 0) for dimensions where candidate information is marked "Not provided"**
    - A score of 0 means poor fit; null means cannot evaluate
    - Base the overall score on the average of NON-NULL dimension scores only
    - Be objective and evidence-based in your scoring
    - Consider both hard requirements (must-haves) and soft preferences (nice-to-haves)
    - Account for transferable skills and adaptability potential
    - In the explanation, mention which dimensions could not be evaluated due to missing data
    - Return ONLY valid JSON, no additional text before or after
    """

    response = client.models.generate_content(model="gemini-2.5-flash", contents=llm_prompt)
    response_text = response.text
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])  # Remove first and last lines

    return json.loads(response_text)


if __name__ == "__main__":
    title = "Software Engineer"
    company = "Tech Corp"
    description = "We are looking for a Software Engineer with experience in Python and web development."
    experience = "3 years as a backend developer using Python and Django."
    education = "Bachelor's degree in Computer Science."
    skills = "Python, Django, REST APIs, SQL"
    qualities = "Team player, problem solver, quick learner"
    interests = "Not interested in software engineer roles"
    print(ai_score_job(experience, education, skills, qualities, None, title, company, description))
