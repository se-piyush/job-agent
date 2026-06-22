"""
agents/crew_tasks.py — CrewAI Task definitions.
Tasks use {placeholder} syntax resolved at kickoff via inputs={}.
"""

from crewai import Agent, Task
from models import SearchResult


def resume_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Tailor Piyush Sharma's resume for the job description below.\n"
            "Generate a complete, valid HTML document — no markdown fences, no commentary.\n\n"
            "Job Description:\n{jd}"
        ),
        expected_output=(
            "A complete HTML document starting with <!DOCTYPE html> and ending with </html>, "
            "with the resume fully tailored to the job description."
        ),
        agent=agent,
    )


def job_search_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Search LinkedIn for Node.js engineering jobs posted in the last 24 hours.\n\n"
            "Make exactly 8 search_jobs calls. "
            "Each call must contain ONLY the fields listed below — do not add any other fields "
            "(no job_type, no extra nulls, no empty strings).\n\n"
            "Calls 1-6 (NCR cities, no work_type field):\n"
            "1. keywords='node.js' location='New Delhi, Delhi, India'     date_posted='past_24_hours' sort_by='date' experience_level='mid_senior' max_pages={max_pages} easy_apply=true \n"
            "2. keywords='node.js' location='New Delhi, Delhi, India'     date_posted='past_24_hours' sort_by='date' experience_level='mid_senior' max_pages={max_pages} easy_apply=false \n"
            "3. keywords='node.js' location='Noida, Uttar Pradesh, India' date_posted='past_24_hours' sort_by='date' experience_level='mid_senior' max_pages={max_pages} easy_apply=true \n"
            "4. keywords='node.js' location='Noida, Uttar Pradesh, India' date_posted='past_24_hours' sort_by='date' experience_level='mid_senior' max_pages={max_pages} easy_apply=false \n"
            "5. keywords='node.js' location='Gurugram, Haryana, India'    date_posted='past_24_hours' sort_by='date' experience_level='mid_senior' max_pages={max_pages} easy_apply=true \n"
            "6. keywords='node.js' location='Gurugram, Haryana, India'    date_posted='past_24_hours' sort_by='date' experience_level='mid_senior' max_pages={max_pages} easy_apply=false \n\n"
            "Calls 7-8 (India remote, must include work_type='remote', no location field):\n"
            "7. keywords='node.js' work_type='remote' date_posted='past_24_hours' location='india' sort_by='date' experience_level='mid_senior' max_pages={max_pages} easy_apply=true \n"
            "8. keywords='node.js' work_type='remote' date_posted='past_24_hours' location='india' sort_by='date' experience_level='mid_senior' max_pages={max_pages} easy_apply=false \n\n"
            "After all 8 calls:\n"
            "- Verify you have made exactly 8 search_jobs calls. If any are missing, make them before continuing.\n"
            "- If the same company has both a backend and a fullstack opening, keep only the backend role.\n"
            "- Deduplicate job IDs.\n"
            "- Return a numbered list: job_id | title | company | location"
        ),
        expected_output=(
            "A numbered list of unique job IDs with title, company, and location.\n"
            "Example:\n1. 1234567890 | Senior Backend Engineer | Stripe | Remote\n"
            "2. 9876543210 | Senior Node.js Developer | Razorpay | Delhi"
        ),
        agent=agent,
    )


def job_filter_task(agent: Agent, search_task: Task) -> Task:
    """Text-output filter task — used by the `search` command."""
    return Task(
        description=(
            "You have a list of LinkedIn job IDs from the search step.\n\n"
            "1. Pick up to 10 jobs whose titles match any of these target roles: "
            "Senior Backend Engineer, Senior Software Engineer, Software Development Engineer III,  Senior Fullstack Engineer, "
            "Tech Lead, Backend Lead, Senior Node.js Developer, Node.js Developer. "
            "Prioritise backend and tech lead titles over fullstack when both appear.\n"
            "2. Call get_job_details for each selected job ID to fetch the full job description.\n"
            "3. Evaluate each full JD against Piyush's profile and the match criteria in your backstory.\n"
            "4. Return only the jobs that are STRONG or MODERATE matches, ranked best-first.\n\n"
            "If no strong matches exist, say so clearly."
        ),
        expected_output=(
            "A ranked shortlist of matching jobs, each formatted as:\n"
            "### [Rank]. [Title] @ [Company] — [Location]\n"
            "**Match:** Strong | Moderate\n"
            "**Stack overlap:** ...\n"
            "**Why:** ...\n"
            "**Job ID:** ...  |  **Posted:** ...\n"
            "---"
        ),
        agent=agent,
        context=[search_task],
    )


def job_filter_task_for_apply(agent: Agent, search_task: Task) -> Task:
    """
    Structured-output filter task — used by the `apply` command.
    Returns a SearchResult Pydantic model (list of MatchedJob) so the caller
    can directly iterate matched jobs and generate resumes without re-parsing.
    """
    return Task(
        description=(
            "You have a list of LinkedIn job IDs from the search step.\n\n"
            "1. Pick up to 8 job IDs whose titles match any of these target roles: "
            "Senior Backend Engineer, Senior Software Engineer, Senior Fullstack Engineer, "
            "Tech Lead, Backend Lead, Senior Node.js Developer, Node.js Developer. "
            "Prioritise backend and tech lead titles over fullstack when both appear.\n"
            "2. Call get_job_details for each selected job ID.\n"
            "3. Evaluate each full JD against Piyush's profile and the match criteria in your backstory.\n"
            "4. For every STRONG or MODERATE match, produce a structured record including:\n"
            "   - rank: integer starting at 1 (best match first)\n"
            "   - title, company, location, job_id\n"
            "   - match_strength: exactly 'Strong' or 'Moderate'\n"
            "   - stack_overlap: list of matching technologies\n"
            "   - why: 1-2 sentence rationale\n"
            "   - jd_text: 150-250 word condensed version of the JD capturing key "
            "responsibilities, required tech stack, and must-haves — this will be used "
            "to tailor Piyush's resume, so be specific about technologies and seniority.\n\n"
            "If no matches are found, return an empty matched_jobs list."
        ),
        expected_output=(
            "A JSON object with a 'matched_jobs' array. Each entry must have: "
            "rank (int), title (str), company (str), location (str), job_id (str), "
            "match_strength ('Strong' or 'Moderate'), stack_overlap (list[str]), "
            "why (str), jd_text (str, 150-250 words)."
        ),
        output_pydantic=SearchResult,
        agent=agent,
        context=[search_task],
    )


def email_task(agent: Agent) -> Task:
    return Task(
        description=(
            "Write a cold outreach email for this job application.\n\n"
            "Company: {company}\n\n"
            "Job Description:\n{jd}"
        ),
        expected_output=(
            "A subject line (prefixed with 'Subject:') followed by the email body, "
            "under 200 words total, personalised to the company and role."
        ),
        agent=agent,
    )
