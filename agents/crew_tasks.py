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
            "Search LinkedIn for senior backend engineering jobs posted in the last 24 hours.\n\n"
            "Run the following three searches (call search_jobs separately for each). "
            "For each call: if work_type is 'any', omit the work_type parameter entirely; "
            "otherwise include work_type={work_type}.\n\n"
            "1. keywords='{keywords}', location='{location}', date_posted={date_posted}, "
            "sort_by=date, experience_level=mid_senior, max_pages={max_pages}\n"
            "2. keywords='Senior Software Engineer TypeScript AWS', location='{location}', "
            "date_posted={date_posted}, sort_by=date, experience_level=mid_senior, max_pages={max_pages}\n"
            "3. keywords='Senior Node.js Developer', location='{location}', "
            "date_posted={date_posted}, sort_by=date, experience_level=mid_senior, max_pages={max_pages}\n\n"
            "Deduplicate job IDs across all searches.\n"
            "Return a numbered list: job_id | title | company | location"
        ),
        expected_output=(
            "A numbered list of unique job IDs with title, company, and location.\n"
            "Example:\n1. 1234567890 | Senior Backend Engineer | Stripe | Remote\n"
            "2. 9876543210 | Senior Node.js Developer | Razorpay | Bangalore"
        ),
        agent=agent,
    )


def job_filter_task(agent: Agent, search_task: Task) -> Task:
    """Text-output filter task — used by the `search` command."""
    return Task(
        description=(
            "You have a list of LinkedIn job IDs from the search step.\n\n"
            "1. Pick up to 10 jobs whose titles look most relevant for a "
            "Senior Backend Engineer (Node.js / TypeScript / AWS background).\n"
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
            "1. Pick up to 8 job IDs whose titles look most relevant for a "
            "Senior Backend Engineer (Node.js / TypeScript / AWS background).\n"
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
