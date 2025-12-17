"""Use Gemini LLM to rate how well scraped jobs match user qualifications."""

from app.job_rating.chatgpt import openai_query

__version__ = 1


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
    system_prompt = """
    You are a career–job matching agent.
    
    Evaluate how well a candidate matches a specific job across the dimensions below.
    Score ONLY when the required data is provided; otherwise return null.
    
    Scoring dimensions (0–10):
    - technical_fit: candidate skills vs job requirements (null if Skills = "Not provided")
    - experience_alignment: relevance of past roles (null if Experience = "Not provided")
    - educational_match: degree and academic alignment (null if Education = "Not provided")
    - interest_match: alignment of interests with role/company (null if Interests = "Not provided")
    
    overall_score:
    - A holistic judgement of candidate–job fit
    - NOT a mathematical average of the other scores
    - Should be broadly consistent with the available dimension scores
    - May weight dimensions unevenly based on job importance
    - If all dimensions are null, set overall_score to null
    
    Rules:
    - 0 = poor fit, null = insufficient information
    - Consider must-haves, nice-to-haves, and transferable skills
    - Be objective and evidence-based
    - Do not invent or infer missing data
    
    Output:
    Return ONLY valid JSON matching this exact schema:
    
    {
      "overall_score": <integer 0–10 or null>,
      "technical_fit": <integer 0–10 or null>,
      "experience_alignment": <integer 0–10 or null>,
      "educational_match": <integer 0–10 or null>,
      "interest_match": <integer 0–10 or null>,
      "explanation": "2–3 concise sentences summarising the assessment and noting any missing data"
    }"""

    user_prompt = f"""
    ### Candidate Profile
    {candidate_profile}
    
    ### Job Details
    {job_details}
    """

    return openai_query(system_prompt, user_prompt)


if __name__ == "__main__":
    title = "Software Engineer"
    company = "Tech Corp"
    description = "We are looking for a Software Engineer with experience in Python and web development."
    experience = "3 years as a backend developer using Python and Django."
    education = "Bachelor's degree in Computer Science."
    skills = "Python, Django, REST APIs, SQL"
    qualities = "Team player, problem solver, quick learner"
    interests = "Not interested in software engineer roles"
    print(ai_score_job(experience, education, skills, qualities, interests, title, company, description))
