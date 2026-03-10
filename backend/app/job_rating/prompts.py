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

Scoring dimensions (0–10):
- technical_fit: candidate skills vs job requirements
- experience_alignment: relevance of past roles
- educational_match: degree and academic alignment
- interest_match: alignment of interests with role/company

Null handling (very important, follow exactly):
- For each dimension:
    - If the *corresponding candidate field string* is exactly "Not provided", you MUST return null for that dimension.
    - If the corresponding candidate field string is anything else (non-empty), you MUST return an integer score 0–10 for that dimension. Do NOT return null in that case, even if information is limited.

Field–dimension mapping:
- Experience -> experience_alignment
- Education -> educational_match
- Skills -> technical_fit
- Interests -> interest_match

overall_score:
- A holistic judgement of candidate–job fit
- NOT a mathematical average of the other scores
- Should be broadly consistent with the available dimension scores
- May weight dimensions unevenly based on job importance
- If at least one dimension has a non-null integer, you MUST output an integer 0–10 (no null allowed).
- Only if all four dimensions are null, set overall_score to null.

Rules:
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
- **Interests**: {user_interests_or_not_provided}
"""

JOB_ONLY_PROMPT_TEMPLATE_V2 = """### Job Details
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

    prompt = prompt_template.format(
        user_experience_or_not_provided=_or_not_provided(user_experience),
        user_education_or_not_provided=_or_not_provided(user_education),
        user_skills_or_not_provided=_or_not_provided(user_skills),
        user_qualities_or_not_provided=_or_not_provided(user_qualities),
        user_interests_or_not_provided=_or_not_provided(user_interests),
    )
    return prompt.replace("{{", "{").replace("}}", "}")


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

    job_template = AiJobPromptTemplate(prompt=JOB_ONLY_PROMPT_TEMPLATE_V2)
    db.add(job_template)

    db.commit()
    db.refresh(system_prompt)
    db.refresh(job_template)

    return system_prompt, job_template


if __name__ == "__main__":
    title = "Ageing Well Manager"
    company = "Age UK Devon"
    description = "Permanent 30–37 hours £30,633 FTE (increasing to £32,304 after probationary period) Exeter / Hybrid / Community Based Age UK Devon is seeking a strategic, forward thinking Ageing Well Manager to lead our work supporting older people to stay independent, connected and well during Later Life. In this leadership role, you will shape and develop services and community activities, ensuring they align with our Strategic Plan and deliver meaningful impact. You’ll drive innovation in community based activities, develop new models of delivery, and lead on monitoring, evaluation and quality improvement. You’ll also build strong partnerships across statutory, voluntary, and community sectors, representing Age UK Devon and identifying opportunities for service growth and sustainability. As a motivating manager, you will provide leadership to staff and volunteers, championing a culture of learning and wellbeing. We’re looking for someone with: Experience of staff and volunteer management Experience of managing services or projects strategically Strong partnership building and communication skills Insight into the needs and challenges faced by older people A proactive, innovative approach to service development Closing date: Sunday 29 March 2026 (midnight) Interviews: 07/04/26 and/or 08/04/26 To apply - Please download and read the Job Description and Recruitment Packs below Complete the Employment Application Form and email to recruitment@ageukdevon.org.uk Complete our Diversity& Equality Form by clicking HERE If you have any questions, please email recruitment@ageukdevon.org.uk or phone us on 0333 241 2340."
    experience = """Sexual Health Promotion Specialist
• Lead for provision of relationship and sex education for young people across Oxfordshire, in group and one-to-one settings. This entails providing secondary school education on topics such as consent, healthy relationships, STIs, contraception, and pleasure amongst other workshop topics.
• Organised, co-ordinated and liaised with secondary schools and adult community organisations to provide bespoke education.
• Managed bookings across the county. I implemented a new online system for booking requests to streamline the process and maximise organisation, alongside providing a new education curriculum.
• Social Media Manager; planning, design, creation and uploading social media content for the service.
• Design and deliver education for vulnerable people including young people, LGBTQ+ people, ethnically diverse groups, people with special educational needs and sex workers.
• Managing challenging and sensitive conversations around sexual health, violence and consent. This includes education sessions focusing on consent and the law, and working with perpetrators of sexual violence. I use knowledge on acts of law, for example, the Sexual Offences Act, and Online Safety Act. There is a heavy focus on reduction of harm from sexual abuse, and safeguarding through the means of education.
• Providing support to victims of sexual assault, with thorough safeguarding assessments, liaison with safeguarding agencies such as the Multi Agency Safeguarding Hub (MASH), and signposting or referring into other services.
• Clinical procedures; community STI testing including venepuncture blood testing, and providing advice.
• Lead Health Promotion Specialist to support a multidisciplinary team, that provide inclusive sexual health care in the community to vulnerable people, such as, drug and alcohol service users, and asylum seekers.
• Production of accessible materials; translated materials and ‘easy read’ guides for people with special educational needs.
• Involvement in Quality Improvement Projects increasing the accessibility of sexual health care.
• Co-lead of a project alongside a specialist doctor, focused on accessibility of HIV prevention medication.
• Regular attendance to NHS meetings, including regular safeguarding meetings.
• I proactively started quarterly Team Supervision support for myself and colleagues continued professional development.
• Liaison with internal and external stakeholders and multidisciplinary team working.

Gastroenterology Dietitian Locum
• I worked at the John Radcliffe Hospital in Oxford with the Gastroenterology Dietetic team in outpatient clinic. This included giving advice over the telephone to patients with IBS, IBD, Coeliac Disease and information on the low oxalate diet.
• I provided assistance on the wards within general medicine to support staff with their workload. There I gave advice to patients and health professional on nutritional management of diseases. I prescribed oral nutritional support and enteral tube feeds.
• Managing challenging conversations, decision making, and problem solving alongside the wider MDT to implement nutritional care. I became skilled at justifying my decisions using my clinical judgement and negotiation skills. I communicated in a professional manner, and we would work as an multidisciplinary team to understand each others decisions and barriers to come up with solutions, to improve nutritional status.
• Thorough assessment of patients clinical condition, to aid with diagnosis using a variety of clinical markers such as blood tests.
• Accurate and clear documentation on clinical systems, and hand overs to Doctors and Nurses in charge.
• Made holistic plans with patients to include SMART goals and considering wider aspects such as mental health and social circumstances.
• Took an active role in decision making and medical care. For example, when patients were on artificial nutrition with poor prognoses and prolonged hospital stays considering the next steps in care are crucial and can be lifechanging for the patients. In these cases I would present all the information and possibilities to patients from a Dietetic point of view empowering them to make careful decisions about their own care.
• Liaison with the wider multi-disciplinary team. If a patient did not have capacity I would be involved in best interest meetings and decisions, which would sometimes involve families of the patients.

Dietitian
• Provided patient care on general wards, whilst focusing on cardiology and oncology wards in particular for oral nutritional support (ONS) and artificial enteral feeding.
• Provided patient care in specialist MDT Gestational Diabetes clinic. This would include carbohydrate counting and portion control, assessing blood records and advising adjustment to diet accordingly. I also provided advice on Metformin and Insulin regimes, with support and agreement from Specialist Diabetes Nurses.
• Provided ad-hoc advise to patients with cancer on the day unit when they attended for chemotherapy. This involved pancreatic cancer patients and advising on pancreatic enzyme replacement therapy, and symptoms related to malabsorption as-well as nutrition support advice and community prescribing of ONS.
• Clinical audit, quantitative and qualitative data collection and analysis, presenting findings to ward staff and offering support with meeting Standard Operating Procedures (SOPs)
• Liaised with catering staff where possible to make special adjustments and meals for patients as required.
• Provided monthly teaching sessions to Health Care Assistants joining the trust. I redesigned this training to make it more interactive with different stations of activities.
• During the COVID pandemic and lockdowns my days could very varied and I assisted other Dietitians or provided cover when people were off sick etc, for example, covering stroke and gastroenterology wards. This required excellent team working skills to ensure we saw high priority patients first and shared the caseload out between the whole team to provide essential cover. This also required me to take on additional out patient-clinics.
• Other speciality areas include oncology, renal and cardiac rehabilitation."""
    education = """University Undergraduate
BSc Hons 2:1 Nutrition and Dietetics

Continual professional development courses
Mental Health, Drug and Alcohol Addiction, Dementia Awareness, Level 2 & 3 Safeguarding, Relationships and Sex Educator, Trainer Development: Delivering to professional and specialist audiences, Early Help Skills: Strengths and Needs Assessments, Volunteer Management, STI and HIV Awareness, Sexual Health for Trans and Gender Diverse people and Females, Assistant Sexual Health Practitioner, Fundamentals of Quality Improvement, Venepuncture
"""
    skills = """Communication
A key strength of mine is being able to foster positive relationships with people with internal and external stakeholders, I am able to deal with sensitive issues, I can effectively communicate in a multidisciplinary team setting, provide advise to patients and service users, train other professionals. I can use digital communication as well, such as social media management. I have good interpersonal skills, I actively listen, provide judgement free space, and I can demonstrate empathy and work with people to find solutions.

Team Player
I thrive in team settings, supporting others, fostering open communication, and helping colleagues succeed.

Working autonomously
I can make decisions independently, and have my own responsibilities within teams and often in specialist areas. 

Attention To Detail
I pay close attention to detail, making sure my work is precise, consistent, and reliable across all aspects of work. For example, clinical examinations. I follow evidenced based practice. I have experience in disease management. I create resources with close attention to detail ensuring accuracy, producing presentations and documents that are engaging and accessible."""
    qualities = """Empathetic, good team player, flexible, adaptable, time management, effective communicator, willing to learn new skills, committed to continuing professional development and evidenced based practice, approachable, proactive, dedicated"""
    interests = """I am interested in roles within the healthcare sector, but not registered healthcare professional roles. I prefer roles in public health and am open to different kind of work in this area. Additionally, other roles within the public sector, such as the ambulance service or councils. I would be interested in roles that include; sexual health, women's health, working with vulnerable people, supporting people with chronic conditions, or providing training. I am very open to new jobs that will utilise my skills. l'm looking for jobs in and around Cardiff, within 20 miles."""
    user_system_prompt = create_system_prompt_with_profile(
        SYSTEM_PROMPT_V2,
        experience,
        education,
        skills,
        qualities,
        interests,
    )
    job_prompt = create_job_only_prompt(JOB_ONLY_PROMPT_TEMPLATE_V2, title, company, description)
    print(openai_query(SYSTEM_PROMPT_V1, user_system_prompt + "\n" + job_prompt))
    print(claude_query(user_system_prompt, job_prompt))
