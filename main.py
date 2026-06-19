"""
main.py — CLI entrypoint for the job application agent system.

Usage:
    python main.py resume --jd jobs/stripe.txt [--company Stripe]
    python main.py resume --jd-text "We are looking for..."

    python main.py email  --jd jobs/stripe.txt --company Stripe

    python main.py search --keywords "Senior Backend Engineer Node.js" \\
                          --location "India" --work-type remote

    python main.py apply  --keywords "Senior Backend Engineer Node.js" \\
                          --location "India" --work-type remote
"""

import sys
import click
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from agents.job_crew import run_resume_crew, run_email_crew, run_job_search_crew, run_apply_crew
from utils.file_utils import read_jd, save_output


_WORK_TYPE_CHOICES = click.Choice(["remote", "on_site", "hybrid", "any"], case_sensitive=False)
_DATE_POSTED_CHOICES = click.Choice(["past_hour", "past_24_hours", "past_week", "past_month"], case_sensitive=False)


@click.group()
def cli():
    """Job Agent — AI-powered resume and email tailoring via CrewAI."""
    pass


# ── resume ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--jd", "jd_path", default=None, help="Path to a .txt file with the job description.")
@click.option("--jd-text", default=None, help="Job description as a string (use quotes).")
@click.option("--company", default="", help="Company name — used in the output filename.")
def resume(jd_path, jd_text, company):
    """Tailor your resume to a job description and save as HTML."""
    jd = _resolve_jd(jd_path, jd_text)

    click.echo("\n🤖 Resume Tailoring Crew running...")
    click.echo(f"   JD length: {len(jd)} chars")

    html = run_resume_crew(jd, company=company)
    output_path = save_output(html, prefix="resume", company=company, ext="html")

    click.echo(f"\n✅ Done! Resume saved to:\n   {output_path}")
    click.echo("\n📄 To convert to PDF:")
    click.echo("   1. Open the file in Chrome")
    click.echo("   2. Ctrl+P → Save as PDF → Margins: None")


# ── email ─────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--jd", "jd_path", default=None, help="Path to a .txt file with the job description.")
@click.option("--jd-text", default=None, help="Job description as a string.")
@click.option("--company", default="", required=True, help="Company name for personalisation.")
def email(jd_path, jd_text, company):
    """Write a tailored cold outreach email for a job application."""
    jd = _resolve_jd(jd_path, jd_text)

    click.echo("\n🤖 Cold Email Crew running...")

    result = run_email_crew(jd, company=company)
    output_path = save_output(result, prefix="email", company=company, ext="txt")

    click.echo(f"\n✅ Done! Email saved to:\n   {output_path}")
    click.echo("\n" + "─" * 60)
    click.echo(result)
    click.echo("─" * 60)


# ── search ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--keywords", default=None,
              help="Search keywords. Default: 'Senior Backend Engineer Node.js TypeScript'")
@click.option("--location", default="",
              help="Location (e.g. 'India', 'Bangalore'). Leave blank for worldwide.")
@click.option("--work-type", default="remote", type=_WORK_TYPE_CHOICES, show_default=True,
              help="Work arrangement filter.")
@click.option("--date-posted", default="past_24_hours", type=_DATE_POSTED_CHOICES, show_default=True,
              help="How recently jobs were posted. 'past_hour' is the tightest filter LinkedIn supports.")
@click.option("--max-pages", default=2, type=click.IntRange(1, 10), show_default=True,
              help="LinkedIn result pages to scan per keyword query (1-10).")
def search(keywords, location, work_type, date_posted, max_pages):
    """Search LinkedIn for matching jobs posted in the last 24 hours.

    Prerequisite — authenticate the LinkedIn MCP server once:

        uvx mcp-server-linkedin --login
    """
    kw = keywords or "Senior Backend Engineer Node.js TypeScript"
    click.echo("\n🔍 Job Search Crew running...")
    click.echo(f"   Keywords   : {kw}")
    click.echo(f"   Location   : {location or 'worldwide'}")
    click.echo(f"   Work type  : {work_type}")
    click.echo(f"   Date posted: {date_posted.replace('_', ' ')}")
    click.echo(f"   Max pages  : {max_pages} per query\n")

    result = run_job_search_crew(
        keywords=kw,
        location=location,
        work_type=work_type,
        date_posted=date_posted,
        max_pages=max_pages,
    )

    output_path = save_output(result, prefix="jobs", company="", ext="txt")
    click.echo(f"\n✅ Done! Results saved to:\n   {output_path}")
    click.echo("\n" + "─" * 60)
    click.echo(result)
    click.echo("─" * 60)


# ── apply ─────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--keywords", default=None,
              help="Search keywords. Default: 'Senior Backend Engineer Node.js TypeScript'")
@click.option("--location", default="",
              help="Location (e.g. 'India', 'Bangalore'). Leave blank for worldwide.")
@click.option("--work-type", default="remote", type=_WORK_TYPE_CHOICES, show_default=True,
              help="Work arrangement filter.")
@click.option("--date-posted", default="past_24_hours", type=_DATE_POSTED_CHOICES, show_default=True,
              help="How recently jobs were posted. 'past_hour' is the tightest filter LinkedIn supports.")
@click.option("--max-pages", default=2, type=click.IntRange(1, 10), show_default=True,
              help="LinkedIn result pages to scan per keyword query (1-10).")
def apply(keywords, location, work_type, date_posted, max_pages):
    """Search LinkedIn, generate a tailored resume per match, and open a dashboard.

    Runs the full pipeline:
      1. Search LinkedIn (past 24 h, mid-senior, filtered by work type)
      2. Match jobs against Piyush's profile
      3. Generate a tailored HTML resume for every matched job
      4. Convert resumes to PDF if playwright is installed
         (pip install playwright && playwright install chromium)
      5. Open an HTML dashboard table — one row per job, linked to its resume

    Prerequisite — authenticate the LinkedIn MCP server once:

        uvx mcp-server-linkedin --login
    """
    kw = keywords or "Senior Backend Engineer Node.js TypeScript"
    click.echo("\n🚀 Apply Crew running...")
    click.echo(f"   Keywords   : {kw}")
    click.echo(f"   Location   : {location or 'worldwide'}")
    click.echo(f"   Work type  : {work_type}")
    click.echo(f"   Date posted: {date_posted.replace('_', ' ')}")
    click.echo(f"   Max pages  : {max_pages} per query\n")

    result = run_apply_crew(
        keywords=kw,
        location=location,
        work_type=work_type,
        date_posted=date_posted,
        max_pages=max_pages,
    )

    if "error" in result:
        click.echo(f"\n❌ {result['error']}", err=True)
        sys.exit(1)

    matched = result.get("matched_jobs", [])
    if not matched:
        click.echo("\n⚠️  No matching jobs found for today. Try again later or broaden your filters.")
        sys.exit(0)

    click.echo(f"\n✅ {len(matched)} job(s) matched. Resumes generated.")

    # Report resume files
    resume_paths = result.get("resume_paths", {})
    for job in matched:
        paths = resume_paths.get(job.job_id, {})
        pdf = paths.get("pdf")
        html = paths.get("html")
        label = str(pdf) if pdf else str(html)
        fmt = "PDF" if pdf else "HTML"
        click.echo(f"   [{fmt}] {job.company} — {job.title}: {label}")

    dashboard = result.get("dashboard_path")
    if dashboard:
        click.echo(f"\n📊 Dashboard: {dashboard}")
        click.echo("   Open in a browser to see all jobs in a table with resume links.")


# ── helpers ───────────────────────────────────────────────────────────────────

def _resolve_jd(jd_path: str, jd_text: str) -> str:
    if jd_path:
        if not Path(jd_path).exists():
            click.echo(f"❌ File not found: {jd_path}", err=True)
            sys.exit(1)
        return read_jd(jd_path)
    elif jd_text:
        return jd_text.strip()
    else:
        click.echo("❌ Provide either --jd <file> or --jd-text '<text>'", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
