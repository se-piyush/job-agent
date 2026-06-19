"""
agents/crew_agents.py — CrewAI Agent definitions for the job application pipeline.
"""

import json
import os
from crewai import Agent, LLM
from profile import PERSONAL, EDUCATION, EXPERIENCE, SKILLS

# ── HTML template as a plain string (not f-string) so CSS braces are literal ──

_RESUME_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Piyush Sharma - Resume</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        @page { size: A4; margin: 0.9cm 1.2cm; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 8.8pt; line-height: 1.32; color: #222; }
        .header { text-align: center; padding-bottom: 5px; border-bottom: 2px solid #1a365d; margin-bottom: 8px; }
        .name { font-size: 19pt; font-weight: 700; color: #1a365d; letter-spacing: 0.5px; }
        .contact-row { font-size: 8.5pt; color: #444; margin-top: 2px; }
        .contact-row a { color: #1a365d; text-decoration: none; }
        .section { margin-bottom: 8px; }
        .section-title { font-size: 9.5pt; font-weight: 700; color: #1a365d; text-transform: uppercase; letter-spacing: 0.6px; border-bottom: 1.5px solid #1a365d; padding-bottom: 2px; margin-bottom: 5px; }
        .exp-item { margin-bottom: 7px; }
        .exp-header { display: flex; justify-content: space-between; align-items: baseline; }
        .company { font-weight: 700; font-size: 9.5pt; color: #1a365d; }
        .date { font-size: 8.5pt; color: #555; white-space: nowrap; }
        .role { font-weight: 600; font-size: 8.8pt; color: #333; font-style: italic; margin-bottom: 1px; }
        .exp-desc { list-style: disc; padding-left: 15px; }
        .exp-desc li { margin-bottom: 1px; text-align: justify; text-align-last: left; }
        .skills-line { font-size: 8.5pt; margin-bottom: 2px; }
        .skill-cat { font-weight: 700; color: #1a365d; }
        .summary { text-align: justify; text-align-last: left; }
        strong { color: #1a365d; }
        .sub-header { display: flex; justify-content: space-between; align-items: baseline; margin-top: 3px; }
        .sub-company { font-weight: 700; font-size: 9pt; color: #2c5282; }
        .edu-line { display: flex; justify-content: space-between; align-items: baseline; }
        .edu-detail { font-size: 8.5pt; color: #444; margin-top: 2px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="name">Piyush Sharma</div>
        <div class="contact-row">
            India | +91 9873302882 |
            <a href="https://www.linkedin.com/in/se-piyusharma/">linkedin.com/in/se-piyusharma</a> |
            <a href="https://github.com/se-piyush">github.com/se-piyush</a>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Professional Summary</div>
        <p class="summary"><!-- TAILORED SUMMARY --></p>
    </div>

    <div class="section">
        <div class="section-title">Technical Skills</div>
        <!-- TAILORED SKILLS LINES using .skills-line and .skill-cat -->
    </div>

    <div class="section">
        <div class="section-title">Professional Experience</div>

        <!-- Abillion -->
        <div class="exp-item">
            <div class="exp-header"><span class="company">Abillion</span><span class="date">Jul 2025 - Nov 2025</span></div>
            <div class="role">Senior Software Engineer</div>
            <ul class="exp-desc"><!-- 3 TAILORED BULLETS --></ul>
        </div>

        <!-- Teamified with sub-clients -->
        <div class="exp-item">
            <div class="exp-header"><span class="company">Teamified</span><span class="date">Mar 2024 - Jul 2025</span></div>
            <div class="role">Senior Software Engineer</div>

            <div class="sub-header"><span class="sub-company">ForteGlobal</span><span class="date">Nov 2024 - Jul 2025</span></div>
            <ul class="exp-desc"><!-- 3 TAILORED BULLETS --></ul>

            <div class="sub-header"><span class="sub-company">Gomist</span><span class="date">Mar 2024 - Nov 2024</span></div>
            <ul class="exp-desc"><!-- 2-3 TAILORED BULLETS --></ul>
        </div>

        <!-- Lifebit -->
        <div class="exp-item">
            <div class="exp-header"><span class="company">Lifebit</span><span class="date">Jun 2022 - Jan 2024</span></div>
            <div class="role">Senior Software Engineer (Contract)</div>
            <ul class="exp-desc"><!-- 2-3 TAILORED BULLETS --></ul>
        </div>

        <!-- OnceHub -->
        <div class="exp-item">
            <div class="exp-header"><span class="company">OnceHub</span><span class="date">Jan 2017 - Jun 2022</span></div>
            <div class="role">Senior Software Engineer (2021-2022) | SDE (2017-2021)</div>
            <ul class="exp-desc"><!-- 2-3 TAILORED BULLETS --></ul>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Education</div>
        <div class="edu-line">
            <span style="font-weight:700;">Bachelor of Technology (B.Tech) in Information Technology</span>
            <span class="date">2012 - 2016</span>
        </div>
        <div class="edu-detail">Guru Gobind Singh Indraprastha University, Delhi</div>
    </div>
</body>
</html>"""


def _llm() -> LLM:
    return LLM(
        model="anthropic/claude-sonnet-4-6",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        max_tokens=4096,
    )


def build_resume_agent() -> Agent:
    profile_json = json.dumps(
        {"personal": PERSONAL, "education": EDUCATION, "experience": EXPERIENCE, "skills": SKILLS},
        indent=2,
    )

    backstory = (
        "You work exclusively on tailoring Piyush Sharma's resume to job descriptions.\n\n"
        "## STRICT RULES\n\n"
        "### Content rules\n"
        "1. Tailor the Professional Summary to mirror the JD's language and priorities — stay truthful.\n"
        "2. Technical Skills — ONLY include categories and items that are directly relevant to the JD. "
        "Drop entire categories with no overlap (e.g. omit Messaging if Kafka is not relevant). "
        "Aim for 4–6 skill lines total; a leaner section frees vertical space for more bullets.\n"
        "3. Page filling — the rendered PDF must fill a full A4 page without overflowing to a second page. "
        "Calibrate bullet counts per role to achieve this:\n"
        "   - Abillion: 2–3 bullets\n"
        "   - ForteGlobal: 3 bullets\n"
        "   - Gomist: 3 bullets\n"
        "   - Lifebit: 2–3 bullets\n"
        "   - OnceHub: 2–3 bullets\n"
        "   If the skills section is short (few lines), use the upper end of the bullet range to fill the page. "
        "Every bullet must be truthful and drawn from the experience bank — no filler.\n"
        "   For Lifebit and OnceHub specifically: pick ONLY the bullets most directly relevant to the JD's "
        "required stack and responsibilities — do not default to the most impressive-sounding bullets, "
        "default to the most relevant ones.\n"
        "4. Bullets must feel natural — outcome/metric first or woven in. Never write 'as measured by'.\n"
        "5. Bold with <strong> keywords and tech terms that match the JD.\n"
        "6. Job role line = title only. No platform descriptors.\n"
        "7. Teamified stays as parent company; ForteGlobal and Gomist as sub-clients using the sub-header HTML pattern.\n"
        "8. Dates must exactly match the template — never alter them.\n"
        "9. LinkedIn and GitHub must be clickable <a href> tags exactly as in the template.\n"
        "10. Education: always use exact education details from profile — never change.\n\n"
        "### Style rules — NEVER change any of these\n"
        "- Font: Inter from Google Fonts\n"
        "- Colors: #1a365d (primary blue), #2c5282 (sub-company), #333, #444, #555, #222\n"
        "- All CSS class names and structure identical to the template\n"
        "- @page size: A4, margin: 0.9cm 1.2cm\n"
        "- Font size: 8.8pt body, 19pt name, 9.5pt section titles and company names\n"
        "- <strong> color: #1a365d (set via CSS)\n"
        "- Spacing, borders, flex layout — all unchanged\n\n"
        "## PIYUSH'S PROFILE (experience bank + skills)\n\n"
        + profile_json
        + "\n\n## HTML TEMPLATE (replicate structure exactly)\n\n"
        + _RESUME_HTML_TEMPLATE
    )

    return Agent(
        role="Resume Tailoring Specialist",
        goal=(
            "Generate a complete, valid tailored HTML resume for Piyush Sharma that mirrors the "
            "job description's language and priorities. Output ONLY the HTML — no explanation, "
            "no markdown fences, no preamble. Start with <!DOCTYPE html> and end with </html>."
        ),
        backstory=backstory,
        llm=_llm(),
        verbose=False,
        allow_delegation=False,
    )


def build_job_search_agent(tools: list = None) -> Agent:
    """
    Searches LinkedIn for senior backend engineering jobs posted in the last 24 hours.
    Requires linkedin MCP tools (search_jobs) injected at runtime.
    """
    return Agent(
        role="LinkedIn Job Scout",
        goal=(
            "Search LinkedIn for senior backend engineering jobs posted in the last 24 hours "
            "that match Piyush Sharma's Node.js / TypeScript / AWS stack. Return a structured "
            "list of job IDs, titles, companies, and locations from the search results."
        ),
        backstory=(
            "You are a specialist at finding relevant engineering job postings on LinkedIn. "
            "Piyush Sharma is a Senior Backend Engineer with 8+ years of experience. "
            "His core stack: Node.js, TypeScript, GraphQL, REST APIs, PostgreSQL, MongoDB, "
            "DynamoDB, Apache Kafka, AWS (Lambda, RDS, S3, Cognito, CloudFront), "
            "Kubernetes, Docker, GitHub Actions, Terraform, OAuth 2.0, JWT, RBAC.\n\n"
            "When searching:\n"
            "- Always use date_posted=past_24_hours\n"
            "- Always use sort_by=date\n"
            "- Use experience_level=mid_senior\n"
            "- Run 2-3 searches with different keyword combinations to maximise coverage:\n"
            "  e.g. 'Senior Backend Engineer Node.js', 'Senior Software Engineer TypeScript AWS', "
            "'Senior Node.js Developer'\n"
            "- Collect all unique job IDs across searches\n"
            "- Return a clean numbered list: job ID | title | company | location"
        ),
        tools=tools or [],
        llm=_llm(),
        verbose=True,
        allow_delegation=False,
    )


def build_job_match_agent(tools: list = None) -> Agent:
    """
    Fetches full job details and scores each against Piyush's profile.
    Requires linkedin MCP tools (get_job_details) injected at runtime.
    """
    profile_json = json.dumps(
        {"experience": EXPERIENCE, "skills": SKILLS},
        indent=2,
    )

    return Agent(
        role="Job Match Evaluator",
        goal=(
            "Fetch the full details of the most promising job candidates and evaluate which ones "
            "genuinely match Piyush Sharma's 8+ years of senior backend engineering background. "
            "Return a ranked shortlist with a clear match rationale for each."
        ),
        backstory=(
            "You are an expert technical recruiter who evaluates job-candidate fit with precision. "
            "You have deep knowledge of backend engineering stacks and can quickly assess whether "
            "a job description aligns with a candidate's experience.\n\n"
            "## PIYUSH'S PROFILE\n\n"
            + profile_json
            + "\n\n"
            "## EVALUATION CRITERIA\n"
            "A job is a STRONG match if it:\n"
            "- Is a senior backend / full-stack backend / platform engineering role\n"
            "- Uses at least 3 of his core technologies: Node.js, TypeScript, AWS, PostgreSQL, "
            "MongoDB, DynamoDB, Kafka, GraphQL, Kubernetes, Terraform\n"
            "- Requires 5-10 years of experience (not entry-level, not director+)\n\n"
            "A job is a WEAK match if it:\n"
            "- Is primarily frontend, mobile, data engineering, or ML/AI engineering\n"
            "- Requires technologies completely outside his stack (e.g. Java, Go, Python-only)\n"
            "- Is a management-only role with no engineering\n\n"
            "## PROCESS\n"
            "1. From the search results, select up to 10 jobs that look most promising by title\n"
            "2. Use get_job_details to fetch the full JD for each selected job\n"
            "3. Evaluate each JD against the criteria above\n"
            "4. Return only STRONG matches, ranked by relevance\n\n"
            "## OUTPUT FORMAT (for each matched job)\n"
            "### [Rank]. [Title] @ [Company] — [Location]\n"
            "**Match:** Strong | Moderate\n"
            "**Stack overlap:** [list matching technologies]\n"
            "**Why:** [2-sentence rationale]\n"
            "**Job ID:** [id]  |  **Posted:** [time ago]\n"
            "---"
        ),
        tools=tools or [],
        llm=_llm(),
        verbose=True,
        allow_delegation=False,
    )


def build_email_agent() -> Agent:
    backstory = (
        f"You write cold outreach emails for {PERSONAL['name']}, a Senior Backend Engineer with 8+ years of experience.\n\n"
        "## TONE\n"
        "Confident but not arrogant. Specific not generic. Like a message from a senior engineer "
        "who knows their worth and respects the reader's time.\n\n"
        "## EXPERIENCE HIGHLIGHTS (pick the most relevant 2-3)\n"
        "- Eliminated data loss at 1,000+ req/s by architecting a Kafka event-driven pipeline at OnceHub\n"
        "- Cut deployment time by 90% via Kubernetes/microservices migration\n"
        "- Reduced dashboard load from 8s to 100ms via pagination\n"
        "- Automated $50K/month in payments via Stripe integration at ForteGlobal\n"
        "- Reduced AWS infra costs by 30% via EC2 → Lambda migration at Lifebit\n"
        "- Built marketplace APIs serving 200K+ MAU at Abillion\n"
        "- Led KYC pipeline and serverless fintech backend at Gomist\n\n"
        "## OUTPUT FORMAT\n"
        "Subject: [subject line]\n\n"
        "[email body]\n\n"
        "Output only the subject line and body. No extra commentary."
    )

    return Agent(
        role="Cold Outreach Email Specialist",
        goal=(
            "Write a concise, personalised cold email that opens with a specific company hook, "
            "highlights 2-3 relevant achievements, has a clear call to action, feels human and "
            "direct, and stays under 200 words."
        ),
        backstory=backstory,
        llm=_llm(),
        verbose=False,
        allow_delegation=False,
    )
