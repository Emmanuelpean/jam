"""Use Gemini LLM to rate how well scraped jobs match user qualifications."""

import datetime as dt
import json
import traceback

import pytest
from google import genai
from sqlalchemy import func

from app import models
from app import utils
from app.config import settings
from app.database import get_db
from app.eis import models as eis_models
from app.service_runner import ServiceRunner

__version__ = 1

client = genai.Client(api_key=settings.gemini_api_key)


def score_scraped_jobs(min_description_length: int = 10) -> models.JobRatingServiceLog:
    """Score all scraped jobs using Gemini LLM.
    :param min_description_length: Minimum job description length to consider"""

    db = next(get_db())
    logger = utils.AppLogger.create_service_logger("llm_job_rating")
    start_time = dt.datetime.now()
    service_log = models.JobRatingServiceLog(run_datetime=start_time)

    try:
        # noinspection PyComparisonWithNone
        scraped_jobs = (
            db.query(eis_models.ScrapedJob)
            .filter(eis_models.ScrapedJob.is_scraped)  # scraped
            .filter(eis_models.ScrapedJob.is_failed.is_(False))  # not failed
            .filter(eis_models.ScrapedJob.job_rating == None)  # not yet rated
            .filter(eis_models.ScrapedJob.is_active)  # active
            .filter(eis_models.ScrapedJob.is_imported.is_(False))  # not imported
            .filter(func.length(eis_models.ScrapedJob.description) > min_description_length)  # description length
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
            kwargs = dict(
                scraped_job_id=scraped_job.id,
                owner_id=owner_id,
                script_version=__version__,
                user_qualification_id=owner_qualifications.id,
            )
            if owner_qualifications and (
                owner_qualifications.experience
                or owner_qualifications.education
                or owner_qualifications.skills
                or owner_qualifications.qualities
            ):
                score = None
                try:
                    logger.info(f"Scoring job ID {scraped_job.id} for owner ID {owner_id}")
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
                        overall_score=score["overall_score"],
                        technical_score=score["technical_fit"],
                        experience_score=score["experience_alignment"],
                        educational_score=score["educational_match"],
                        interest_score=score["interest_match"],
                        feedback=score["explanation"],
                        is_success=True,
                        **kwargs,
                    )
                    db.add(job_rating)
                    db.commit()
                except Exception as exception:
                    tb = traceback.format_exc()
                    logger.exception(f"Error in rating workflow: {exception}")
                    # noinspection PyArgumentList
                    job_rating = models.JobRating(
                        is_success=False,
                        error=f"Error scoring job: {exception}\n{tb}\nRaw response is {score}",
                        **kwargs,
                    )
                    db.add(job_rating)
                    db.commit()

        # Log final statistics
        service_log.run_duration = (dt.datetime.now() - start_time).total_seconds()
        service_log.is_success = True

    except Exception as exception:
        logger.exception(f"Critical error in rating workflow: {exception}")
        service_log.run_duration = (dt.datetime.now() - start_time).total_seconds()
        service_log.is_success = False
        service_log.error_message = str(exception)
    finally:
        logger.info("Finished workflow")

    db.commit()
    return service_log


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


class LlmJobRatingServiceRunner(ServiceRunner):
    """Service runner for the LLM job rating service."""

    service_function = score_scraped_jobs
    service_name = "llm_job_rating"
    period_hours = 6.0


if __name__ == "__main__":
    # title = "Software Engineer"
    # company = "Tech Corp"
    # description = "We are looking for a Software Engineer with experience in Python and web development."
    # experience = "3 years as a backend developer using Python and Django."
    # education = "Bachelor's degree in Computer Science."
    # skills = "Python, Django, REST APIs, SQL"
    # qualities = "Team player, problem solver, quick learner"
    # interests = "Not interested in software engineer roles"
    # print(ai_score_job(experience, education, skills, qualities, None, title, company, description))
    #
    # service_runner = LlmJobRatingServiceRunner()
    # service_runner.start_runner(1)

    score_scraped_jobs(10)
