"""Use Gemini LLM to rate how well scraped jobs match user qualifications."""

from sqlalchemy.orm import Session

from app.job_rating.chatgpt import openai_query
from app.job_rating.claude import claude_query
from app.job_rating.models import AiSystemPrompt, AiJobPromptTemplate


# -------------------------------------------------------- V1 ---------------------------------------------------------


SYSTEM_PROMPT_V1 = """
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


JOB_PROMPT_TEMPLATE_V1 = """### Candidate Profile
- **Experience**: {user_experience_or_not_provided}
- **Education**: {user_education_or_not_provided}
- **Skills**: {user_skills_or_not_provided}
- **Qualities**: {user_qualities_or_not_provided}
- **Interests**: {user_interests_or_not_provided}

### Job Details
- **Title**: {job_title_or_not_provided}
- **Company**: {job_company_or_not_provided}
- **Description**: {job_description_or_not_provided}
"""

# -------------------------------------------------------- V2 ---------------------------------------------------------


SYSTEM_PROMPT_V2 = """
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

{{
  "overall_score": <integer 0–10 or null>,
  "technical_fit": <integer 0–10 or null>,
  "experience_alignment": <integer 0–10 or null>,
  "educational_match": <integer 0–10 or null>,
  "interest_match": <integer 0–10 or null>,
  "explanation": "2–3 concise sentences summarising the assessment and noting any missing data"
}}

### Candidate Profile
- **Experience**: {user_experience_or_not_provided}
- **Education**: {user_education_or_not_provided}
- **Skills**: {user_skills_or_not_provided}
- **Qualities**: {user_qualities_or_not_provided}
- **Interests**: {user_interests_or_not_provided}"""

JOB_ONLY_PROMPT_TEMPLATE_V1 = """### Job Details
- **Title**: {job_title_or_not_provided}
- **Company**: {job_company_or_not_provided}
- **Description**: {job_description_or_not_provided}
"""


def _or_not_provided(value: str | None) -> str:
    """Return "Not provided" if value is None or empty, otherwise strip and return."""

    return value.strip() if value and value.strip() else "Not provided"


def create_system_prompt_with_profile(
    prompt_template: str,
    user_experience: str | None,
    user_education: str | None,
    user_skills: str | None,
    user_qualities: str | None,
    user_interests: str | None,
) -> str:
    """Build a system prompt with the candidate profile embedded.
    :param prompt_template: System prompt template with candidate profile placeholders.
    :param user_experience: User's experience description
    :param user_education: User's education description
    :param user_skills: User's skills description
    :param user_qualities: User's qualities description
    :param user_interests: User's interests description
    :return: System prompt string with candidate profile filled in."""

    return prompt_template.format(
        user_experience_or_not_provided=_or_not_provided(user_experience),
        user_education_or_not_provided=_or_not_provided(user_education),
        user_skills_or_not_provided=_or_not_provided(user_skills),
        user_qualities_or_not_provided=_or_not_provided(user_qualities),
        user_interests_or_not_provided=_or_not_provided(user_interests),
    )


def create_job_only_prompt(
    prompt_template: str,
    job_title: str | None,
    job_company: str | None,
    job_description: str | None,
) -> str:
    """Build a user message containing only job details.
    :param prompt_template: Job-only prompt template.
    :param job_title: Job title
    :param job_company: Job company
    :param job_description: Job description
    :return: Prompt string containing job details only."""

    return prompt_template.format(
        job_title_or_not_provided=_or_not_provided(job_title),
        job_company_or_not_provided=_or_not_provided(job_company),
        job_description_or_not_provided=_or_not_provided(job_description),
    )


def seed_ai_prompts(db: Session) -> tuple[AiSystemPrompt, AiJobPromptTemplate]:
    """Seed the database with initial AI prompts if they don't exist.
    :param db: Database session
    :return: Tuple of (AiSystemPrompt, AiJobPromptTemplate) instances"""

    system_prompt = AiSystemPrompt(prompt=SYSTEM_PROMPT_V2)
    db.add(system_prompt)

    job_template = AiJobPromptTemplate(prompt=JOB_ONLY_PROMPT_TEMPLATE_V1)
    db.add(job_template)

    db.commit()
    db.refresh(system_prompt)
    db.refresh(job_template)

    return system_prompt, job_template


if __name__ == "__main__":
    title = "Software Engineer"
    company = "Tech Corp"
    description = "We are looking for a Software Engineer with experience in Python and web development."
    experience = "3 years as a backend developer using Python and Django."
    education = "Bachelor's degree in Computer Science."
    skills = "Python, Django, REST APIs, SQL"
    qualities = "Team player, problem solver, quick learner"
    interests = "Not interested in software engineer roles"
    user_system_prompt = create_system_prompt_with_profile(
        SYSTEM_PROMPT_V2,
        experience,
        education,
        skills,
        qualities,
        interests,
    )
    job_prompt = create_job_only_prompt(JOB_ONLY_PROMPT_TEMPLATE_V1, title, company, description)
    print(openai_query(SYSTEM_PROMPT_V1, user_system_prompt + "\n" + job_prompt))
    print(claude_query(user_system_prompt, job_prompt))
