import datetime as dt
import json
import traceback

from google import genai

from app import models
from app import utils
from app.config import settings
from app.database import get_db
from app.eis import models as eis_models

__version__ = 1

client = genai.Client(api_key=settings.gemini_api_key)


def score_jobs() -> models.JobRatingServiceLog:
    """Score all scraped jobs using Gemini LLM."""

    db = next(get_db())
    logger = utils.AppLogger.create_service_logger("llm_job_rating")
    start_time = dt.datetime.now()
    service_log = models.JobRatingServiceLog(run_datetime=start_time)

    try:
        scraped_jobs = (
            db.query(eis_models.ScrapedJob)
            .filter(eis_models.ScrapedJob.is_scraped)
            .filter(eis_models.ScrapedJob.job_rating)
            .all()
        )

        for scraped_job in scraped_jobs:
            owner_id = scraped_job.owner_id
            owner_qualifications = (
                db.query(models.UserQualification)
                .filter(models.UserQualification.owner_id == owner_id)
                .order_by(models.UserQualification.modified_at.desc())
                .first()
            )
            if owner_qualifications and (
                owner_qualifications.experience
                or owner_qualifications.education
                or owner_qualifications.skills
                or owner_qualifications.qualities
            ):
                try:
                    score = ai_score_job(
                        owner_qualifications.experience,
                        owner_qualifications.education,
                        owner_qualifications.skills,
                        owner_qualifications.qualities,
                        owner_qualifications.interests,
                        scraped_job.title,
                        scraped_job.company,
                        scraped_job.description,
                    )
                    # noinspection PyArgumentList
                    job_rating = models.JobRating(
                        score=score["overall_score"],
                        scraped_job_id=scraped_job.id,
                        owner_id=owner_id,
                        feedback=score["explanation"],
                        script_version=__version__,
                        user_qualification_id=owner_qualifications.id,
                    )
                    db.add(job_rating)
                    db.commit()
                except Exception as exception:
                    tb = traceback.format_exc()
                    # noinspection PyArgumentList
                    err = models.JobRaringServiceError(
                        error_type=type(exception).__name__,
                        message=str(exception),
                        traceback=tb,
                        service_log_id=service_log.id,
                    )
                    db.add(err)
                    db.commit()

        # Log final statistics
        service_log.run_duration = (dt.datetime.now() - start_time).total_seconds()
        service_log.is_success = True

    except Exception as exception:
        logger.exception(f"Critical error in scraping workflow: {exception}")
        service_log.run_duration = (dt.datetime.now() - start_time).total_seconds()
        service_log.is_success = False
        service_log.error_message = str(exception)
    finally:
        logger.info("Finished workflow")

    db.commit()
    return service_log


def ai_score_job(
    user_experience: str,
    user_education: str,
    user_skills: str,
    user_qualities: str,
    user_interests: str,
    job_title: str,
    job_company: str,
    job_description: str,
) -> dict:
    """User Gemini LLM to score how well a user's qualifications match a scraped job.
    :param user_experience: User's experience description
    :param user_education: User's education description
    :param user_skills: User's skills description
    :param user_qualities: User's qualities description
    :param user_interests: User's interests description
    :param job_title: Job title
    :param job_company: Job company
    :param job_description: Job description
    :return: JSON string with overall score and explanation."""

    llm_prompt = f"""
    You are an expert career matching agent specializing in evaluating candidate-job compatibility. Your task is to analyze how well a candidate matches a specific job opportunity across multiple dimensions.
    
    ## Input Information
    
    ### Candidate Profile
    - **Experience**: {user_experience}
    - **Education**: {user_education}
    - **Skills**: {user_skills}
    - **Qualities**: {user_qualities}
    - **Interests**: {user_interests}
    
    ### Job Details
    - **Title**: {job_title}
    - **Company**: {job_company}
    - **Description**: {job_description}
    
    ## Evaluation Framework
    
    Assess the candidate across these dimensions and provide a score (0-10) for each:
    
    1. **Technical Fit** (0-10): Match between candidate's technical skills and job requirements
    2. **Experience Alignment** (0-10): Relevance of past roles to the position's responsibilities
    3. **Educational Match** (0-10): Degree requirements and academic background alignment
    4. **Interest Match** (0-10): Alignment of candidate's interests with job role and company culture
    5. **Overall Score** (0-10): Holistic assessment of candidate-job fit
    
    ## Output Format
    
    Return your assessment as valid JSON with this exact structure:
    
    {{
        "overall_score": <integer 0-10>,
        "technical_fit": <integer 0-10>,
        "experience_alignment": <integer 0-10>,
        "educational_match": <integer 0-10>,
        "interest_match": <integer 0-10>,
        "explanation": "<2-3 sentences explaining your recommendation and any important considerations>"
    }}
    
    ## Evaluation Guidelines
    
    - Be objective and evidence-based in your scoring
    - Consider both hard requirements (must-haves) and soft preferences (nice-to-haves)
    - Account for transferable skills and adaptability potential
    - Flag any deal-breakers or critical mismatches
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
    print(ai_score_job(experience, education, skills, qualities, interests, title, company, description))
