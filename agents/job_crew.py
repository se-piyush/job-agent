"""
agents/job_crew.py — Crew factory functions.
Each function builds a Crew, kicks it off, and returns the output.
"""

from pathlib import Path
from crewai import Crew, Process
from mcp import StdioServerParameters
from agents.crew_agents import (
    build_resume_agent,
    build_email_agent,
    build_job_search_agent,
    build_job_match_agent,
)
from agents.crew_tasks import (
    resume_task,
    email_task,
    job_search_task,
    job_filter_task,
    job_filter_task_for_apply,
)


_MCP_PARAMS = StdioServerParameters(
    command="uvx",
    args=["mcp-server-linkedin@latest"],
    env={"UV_HTTP_TIMEOUT": "300"},
)


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()


# ── Resume ─────────────────────────────────────────────────────────────────────

def run_resume_crew(jd: str, company: str = "") -> str:
    agent = build_resume_agent()
    task = resume_task(agent)
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff(inputs={"jd": jd, "company": company})
    return _strip_fences(str(result))


# ── Email ──────────────────────────────────────────────────────────────────────

def run_email_crew(jd: str, company: str = "") -> str:
    agent = build_email_agent()
    task = email_task(agent)
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True,
    )
    result = crew.kickoff(inputs={"jd": jd, "company": company})
    return str(result).strip()


# ── Job search (text report) ───────────────────────────────────────────────────

def run_job_search_crew(
    keywords: str = "Senior Backend Engineer Node.js TypeScript",
    location: str = "",
    work_type: str = "remote",
    date_posted: str = "past_24_hours",
    max_pages: int = 2,
) -> str:
    """
    Searches LinkedIn for matching jobs (past 24 hours) and returns a
    formatted text report.

    Prerequisite: uvx mcp-server-linkedin --login  (run once to authenticate)
    """
    from crewai_tools import MCPServerAdapter

    with MCPServerAdapter(_MCP_PARAMS) as mcp:
        job_tools = [t for t in mcp if t.name in {"search_jobs", "get_job_details"}]

        search_agent = build_job_search_agent(tools=job_tools)
        match_agent = build_job_match_agent(tools=job_tools)

        s_task = job_search_task(search_agent)
        m_task = job_filter_task(match_agent, search_task=s_task)

        crew = Crew(
            agents=[search_agent, match_agent],
            tasks=[s_task, m_task],
            process=Process.sequential,
            verbose=True,
        )

        result = crew.kickoff(inputs={
            "keywords": keywords,
            "location": location,
            "work_type": work_type,
            "date_posted": date_posted,
            "max_pages": max_pages,
        })

    return str(result).strip()


# ── Apply (search + resumes + dashboard) ──────────────────────────────────────

def run_apply_crew(
    keywords: str = "Senior Backend Engineer Node.js TypeScript",
    location: str = "",
    work_type: str = "remote",
    date_posted: str = "past_24_hours",
    max_pages: int = 2,
) -> dict:
    """
    Full pipeline: LinkedIn search → profile match → tailored resume per job
    → HTML dashboard table.

    Returns:
        {
            "matched_jobs": list[MatchedJob],
            "resume_paths": {job_id: {"html": Path, "pdf": Path|None}},
            "dashboard_path": Path,
        }
    """
    from crewai_tools import MCPServerAdapter
    from utils.file_utils import save_output, build_output_path
    from utils.pdf_utils import html_string_to_pdf
    from utils.dashboard import generate_dashboard

    # ── Phase 1: search + structured match ────────────────────────────────────
    with MCPServerAdapter(_MCP_PARAMS) as mcp:
        job_tools = [t for t in mcp if t.name in {"search_jobs", "get_job_details"}]

        search_agent = build_job_search_agent(tools=job_tools)
        match_agent = build_job_match_agent(tools=job_tools)

        s_task = job_search_task(search_agent)
        m_task = job_filter_task_for_apply(match_agent, search_task=s_task)

        crew = Crew(
            agents=[search_agent, match_agent],
            tasks=[s_task, m_task],
            process=Process.sequential,
            verbose=True,
        )

        crew_result = crew.kickoff(inputs={
            "keywords": keywords,
            "location": location,
            "work_type": work_type,
            "date_posted": date_posted,
            "max_pages": max_pages,
        })

    # ── Parse structured output ────────────────────────────────────────────────
    if not crew_result.pydantic:
        return {"error": "Match agent did not return structured output.", "matched_jobs": []}

    matched_jobs = crew_result.pydantic.matched_jobs

    if not matched_jobs:
        return {"matched_jobs": [], "resume_paths": {}, "dashboard_path": None}

    # ── Phase 2: generate a tailored resume for each matched job ───────────────
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    resume_paths: dict = {}
    for job in matched_jobs:
        html_str = run_resume_crew(jd=job.jd_text, company=job.company)
        pdf_out = build_output_path("resume", job.company, "pdf")
        pdf_path = html_string_to_pdf(html_str, pdf_out)
        if pdf_path:
            resume_paths[job.job_id] = {"html": None, "pdf": pdf_path}
        else:
            html_path = Path(save_output(html_str, prefix="resume", company=job.company, ext="html"))
            resume_paths[job.job_id] = {"html": html_path, "pdf": None}

    # ── Phase 3: generate dashboard ───────────────────────────────────────────
    dashboard_path = generate_dashboard(
        jobs=matched_jobs,
        resume_paths=resume_paths,
        output_dir=output_dir,
        search_meta={"keywords": keywords, "location": location, "work_type": work_type, "date_posted": date_posted},
    )

    return {
        "matched_jobs": matched_jobs,
        "resume_paths": resume_paths,
        "dashboard_path": dashboard_path,
    }
