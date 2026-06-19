# Job Agent

An AI-powered job application pipeline for Piyush Sharma. Searches LinkedIn for matching roles, tailors resumes to each job description, generates cold outreach emails, and produces a single-click application dashboard — all from the CLI.

Built with [CrewAI](https://github.com/joaomdmoura/crewAI) for agent orchestration and [Claude](https://www.anthropic.com/claude) (claude-sonnet-4-6) as the LLM backbone.

---

## What it does

| Command | What happens |
|---|---|
| `resume` | Tailors your resume to a specific job description and saves it as a PDF |
| `email` | Writes a personalised cold outreach email for a role |
| `search` | Searches LinkedIn for matching jobs and shows a ranked shortlist |
| `apply` | Runs the full pipeline: search → match → generate one PDF resume per job → HTML dashboard table |

---

## Project structure

```
job-agent/
├── agents/
│   ├── crew_agents.py     # CrewAI Agent definitions (resume, email, job search, job match)
│   ├── crew_tasks.py      # CrewAI Task definitions with input placeholders
│   └── job_crew.py        # Crew factory functions called by main.py
├── utils/
│   ├── file_utils.py      # File I/O helpers (read JD, save output, slugify)
│   ├── dashboard.py       # Generates the HTML application tracker table
│   └── pdf_utils.py       # Optional HTML → PDF conversion via Playwright
├── output/                # All generated files land here
├── models.py              # Pydantic models for structured CrewAI task output
├── profile.py             # Master experience bank — update this when your CV changes
├── main.py                # Click CLI entrypoint
├── requirements.txt
├── .env.example
└── .env                   # ANTHROPIC_API_KEY (never commit)
```

---

## Requirements

- **Python 3.10 – 3.13** (crewai does not support Python 3.14+)
- **`uv`** — required for managing Python versions and running the LinkedIn MCP server
- **Playwright + Chromium** — required for PDF generation (`resume` and `apply` commands)

## Setup

### 1 — Create a Python 3.12 virtual environment

> Skip this if you already have a Python 3.10–3.13 venv active.

```bash
# Download Python 3.12 and create a local venv (uv handles both)
uv python install 3.12
uv venv --python 3.12 .venv

# Activate (run this every time you open a new terminal)
.venv\Scripts\activate
```

### 2 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `crewai[anthropic]` (the `[anthropic]` extra) is required — it installs the native Anthropic provider that CrewAI uses to call Claude. Plain `crewai` without the extra will fail at runtime.

### 3 — Install Playwright's Chromium browser

PDF generation uses a headless Chromium browser. Run this once after `pip install`:

```bash
playwright install chromium
```

Without this step `resume` falls back to saving HTML and `apply` dashboard links will be HTML-only.

### 4 — Add your Anthropic API key

```bash
cp .env.example .env
# Edit .env and set:
# ANTHROPIC_API_KEY=sk-ant-...
```

### 5 — (For `search` and `apply` only) Authenticate the LinkedIn MCP server

The LinkedIn search feature uses [linkedin-mcp-server](https://github.com/stickerdaniel/linkedin-mcp-server), which controls a real browser session. You need `uv` installed and a one-time login:

```bash
# Open a browser and log in to LinkedIn
uvx mcp-server-linkedin --login
```

Credentials are stored at `~/.linkedin-mcp/profile/` and reused on subsequent runs.

> **Account risk:** LinkedIn's Terms of Service prohibit automated access. Use on your own account at your own risk.

---

## Commands

### `resume` — Tailor resume to a JD

```bash
python main.py resume --jd path/to/jd.txt --company Stripe
python main.py resume --jd-text "We are looking for a Senior Backend Engineer..." --company Stripe
```

Outputs `output/resume_stripe_YYYYMMDD.pdf` — a ready-to-send PDF generated via headless Chromium. If Playwright is not installed, falls back to saving an HTML file instead.

---

### `email` — Write a cold outreach email

```bash
python main.py email --jd path/to/jd.txt --company Stripe
python main.py email --jd-text "We are looking for..." --company Stripe
```

Outputs `output/email_stripe_YYYYMMDD.txt` and prints the email to the terminal.

---

### `search` — Find matching jobs on LinkedIn

```bash
python main.py search \
  --keywords "Senior Backend Engineer Node.js" \
  --location "India" \
  --work-type remote \
  --max-pages 2
```

| Option | Default | Description |
|---|---|---|
| `--keywords` | `Senior Backend Engineer Node.js TypeScript` | LinkedIn search query |
| `--location` | _(worldwide)_ | Country, city, or leave blank |
| `--work-type` | `remote` | `remote` · `on_site` · `hybrid` · `any` |
| `--date-posted` | `past_24_hours` | `past_hour` · `past_24_hours` · `past_week` · `past_month` |
| `--max-pages` | `2` | Pages to scan per keyword query (1–10) |

Runs three keyword variations to maximise coverage, deduplicates results, fetches full job details for the top candidates, and ranks them against your profile. Outputs a formatted shortlist to the terminal and saves it to `output/jobs_YYYYMMDD.txt`.

---

### `apply` — Full pipeline: search → resumes → dashboard

```bash
python main.py apply \
  --keywords "Senior Backend Engineer Node.js" \
  --location "India" \
  --work-type remote \
  --max-pages 2
```

Same options as `search`. What it does end-to-end:

1. **Search** — queries LinkedIn with three keyword variations (mid-senior, filtered by work type and date)
2. **Match** — fetches full JDs for the top 8 candidates, scores each against your Node.js / TypeScript / AWS / Kafka / Kubernetes stack
3. **Resumes** — generates a tailored, one-page PDF resume for every strong/moderate match (HTML fallback if Playwright is missing)
4. **Dashboard** — writes `output/applications_<timestamp>.html`

#### Dashboard table

Open the dashboard HTML in any browser. Each row is one matched job:

| # | Company | Title / Location | Match | Stack overlap | Why it fits | Actions |
|---|---|---|---|---|---|---|
| 1 | Stripe | Senior Backend Engineer / Remote | 🟢 Strong | Node.js, TypeScript, Kafka | Event-driven architecture... | 📄 PDF · 🔗 Apply |

"Apply" links directly to the LinkedIn job posting. "PDF" / "HTML" links open the tailored resume.

---

## Updating your profile

All experience data lives in `profile.py`. Edit it when:
- You start or leave a role (update `EXPERIENCE`)
- Your tech stack changes (update `SKILLS`)
- Your contact details change (update `PERSONAL`)

The resume and email agents read directly from `profile.py` at runtime — no other files need changing.

---

## How agents are wired

```
main.py (Click CLI)
    └─ job_crew.py          ← Crew factory functions
           ├─ crew_agents.py  ← CrewAI Agent definitions (role / goal / backstory / LLM)
           └─ crew_tasks.py   ← CrewAI Task definitions (description / expected_output)

LinkedIn search/apply commands also open an MCPServerAdapter context:
    MCPServerAdapter → uvx mcp-server-linkedin → search_jobs / get_job_details tools
```

To add a new agent, create a builder function in `crew_agents.py`, a task factory in `crew_tasks.py`, a crew function in `job_crew.py`, and wire a new Click command in `main.py`.

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Claude API key from [console.anthropic.com](https://console.anthropic.com) |
