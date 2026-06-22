# Job Agent

An AI-powered job application pipeline for Piyush Sharma. Searches LinkedIn for matching roles, tailors resumes to each job description, generates cold outreach emails, and produces a single-click application dashboard — all from the CLI.

Built with [CrewAI](https://github.com/joaomdmoura/crewAI) for agent orchestration. Uses a **tiered LLM strategy** — Claude Haiku for the resume agent (precise HTML output), Groq free tier for everything else — keeping the cost per full pipeline run under $0.02.

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
│   ├── crew_agents.py     # Agent definitions + per-agent LLM routing
│   ├── crew_tasks.py      # CrewAI Task definitions with input placeholders
│   └── job_crew.py        # Crew factory functions called by main.py
├── utils/
│   ├── file_utils.py      # File I/O helpers (read JD, save output, slugify)
│   ├── dashboard.py       # Generates the HTML application tracker table
│   └── pdf_utils.py       # HTML → PDF conversion via Playwright
├── output/                # All generated files land here
├── models.py              # Pydantic models for structured CrewAI task output
├── profile.py             # Master experience bank — update this when your CV changes
├── main.py                # Click CLI entrypoint
├── requirements.txt
├── .env.example
└── .env                   # API keys (never commit)
```

---

## Requirements

- **Python 3.10 – 3.13** (crewai does not support Python 3.14+)
- **`uv`** — required for managing Python versions and running the LinkedIn MCP server
- **Playwright + Chromium** — required for PDF generation (`resume` and `apply` commands)

---

## Setup

### 1 — Create a Python 3.12 virtual environment

> Skip this if you already have a Python 3.10–3.13 venv active.

```bash
uv python install 3.12
uv venv --python 3.12 .venv

# Activate (run every time you open a new terminal)
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
```

### 2 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** Two extras are required — `crewai[anthropic,litellm]`. The `[anthropic]` extra installs the native Anthropic provider used by the resume agent. The `[litellm]` extra enables Groq, Together AI, Fireworks, OpenRouter, and any other non-native provider. Plain `crewai` without these extras will fail at runtime.

### 3 — Install Playwright's Chromium browser

PDF generation uses headless Chromium. Run this once after `pip install`:

```bash
playwright install chromium
```

Without this step `resume` falls back to saving HTML and `apply` dashboard links will be HTML-only.

### 4 — Configure API keys

```bash
cp .env.example .env
```

Edit `.env` and fill in the keys for the providers you plan to use:

```env
# Required for the resume agent (default: Haiku)
ANTHROPIC_API_KEY=sk-ant-...

# Required for search / match / email agents (default: Groq free tier)
# Sign up free at https://console.groq.com
GROQ_API_KEY=gsk_...
```

Both keys are needed for a default out-of-the-box run. If you override all agents to a single provider (see [LLM configuration](#llm-configuration)), you only need that provider's key.

### 5 — (For `search` and `apply` only) Authenticate the LinkedIn MCP server

The LinkedIn search feature uses [linkedin-mcp-server](https://github.com/stickerdaniel/linkedin-mcp-server), which controls a real browser session. You need `uv` installed and a one-time login:

```bash
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

Outputs `output/resume_stripe_YYYYMMDD.pdf` — a ready-to-send PDF generated via headless Chromium. Falls back to HTML if Playwright is not installed.

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

Runs three keyword variations to maximise coverage, deduplicates results, fetches full job details for the top candidates, and ranks them against your profile. Saves to `output/jobs_YYYYMMDD.txt`.

---

### `apply` — Full pipeline: search → resumes → dashboard

```bash
python main.py apply \
  --keywords "Senior Backend Engineer Node.js" \
  --location "India" \
  --work-type remote \
  --max-pages 2
```

Same options as `search`. End-to-end:

1. **Search** — queries LinkedIn with three keyword variations (mid-senior, filtered by work type and date)
2. **Match** — fetches full JDs for the top candidates, scores each against your stack
3. **Resumes** — generates a tailored one-page PDF resume per strong/moderate match
4. **Dashboard** — writes `output/applications_<timestamp>.html`

Open the dashboard in any browser. Each row is one matched job with a direct link to its tailored resume and the LinkedIn application page.

---

## LLM configuration

Each agent uses its own default model tuned for cost vs. quality. You can override any tier without touching code.

### Default tier assignment

| Agent | Default model | Rationale | Est. cost/run |
|---|---|---|---|
| Resume | `anthropic/claude-haiku-4-5-20251001` | Strict HTML with 10+ rules — needs reliable instruction following | ~$0.014 |
| Job Search | `anthropic/claude-haiku-4-5-20251001` | Multi-turn tool calling (LinkedIn MCP) — context grows with each tool result and exceeds Groq's free 12k TPM | ~$0.005 |
| Job Match | `anthropic/claude-haiku-4-5-20251001` | Fetches 8-10 full JDs via tool calls — large accumulated context | ~$0.010 |
| Email | `groq/llama-3.3-70b-versatile` | Short free-form text, no tool calls — fits Groq's free tier comfortably | $0.00 |

**Total per full `apply` run: ~$0.029 + $0.014 per matched job** (search+match once, one resume per match).

> **Why not Groq for search/match?** Groq's free tier allows 12,000 tokens/minute. A single tool-calling pass (system prompt + profile JSON + accumulated LinkedIn tool results) can exceed this in one request. Use `SEARCH_MODEL` / `MATCH_MODEL` env vars to override if you have a paid Groq plan.

### Override priority

```
CLI --model flag  →  per-agent env var  →  LLM_MODEL env var  →  agent default
```

### Per-agent env vars (`.env`)

Override individual agents without changing anything else:

```env
RESUME_MODEL=anthropic/claude-haiku-4-5-20251001   # or claude-sonnet-4-6 for best quality
SEARCH_MODEL=groq/llama-3.3-70b-versatile
MATCH_MODEL=groq/llama-3.3-70b-versatile
EMAIL_MODEL=groq/llama-3.3-70b-versatile
```

### Force all agents to one model (CLI)

```bash
# Use Claude Sonnet for everything (highest quality, higher cost)
python main.py --model anthropic/claude-sonnet-4-6 resume --jd jd.txt

# Use a local Ollama model for everything (free, needs GPU)
python main.py --model ollama/qwen2.5:14b resume --jd jd.txt
```

### Supported providers

| Provider prefix | API key env var | Notes |
|---|---|---|
| `anthropic/` | `ANTHROPIC_API_KEY` | Claude models |
| `groq/` | `GROQ_API_KEY` | Free tier at [console.groq.com](https://console.groq.com); 128k context |
| `ollama/` | — | Local models via [Ollama](https://ollama.com); set `OLLAMA_BASE_URL` if not localhost |
| `together_ai/` | `TOGETHER_API_KEY` | Hosted open-source models |
| `fireworks_ai/` | `FIREWORKS_API_KEY` | Fast hosted inference |
| `openrouter/` | `OPENROUTER_API_KEY` | Multi-provider router |

#### Ollama model names

Valid Ollama model strings (note the colon, not a dot):

```
ollama/qwen2.5:7b      # 8 GB VRAM — borderline for resume task
ollama/qwen2.5:14b     # 16 GB VRAM — minimum recommended
ollama/qwen2.5:32b     # 24 GB VRAM — reliable
ollama/llama3.3:70b    # 48 GB VRAM — best open-source quality
```

Pull before use: `ollama pull qwen2.5:14b`

Ollama's context window defaults to 4096 tokens, which is too small for the resume agent's backstory (~3,300 tokens + JD). The code automatically sets `num_ctx=16384` for all `ollama/` models.

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | If using `anthropic/` models | From [console.anthropic.com](https://console.anthropic.com) |
| `GROQ_API_KEY` | If using `groq/` models | Free at [console.groq.com](https://console.groq.com) |
| `RESUME_MODEL` | No | Override resume agent model (default: Haiku) |
| `SEARCH_MODEL` | No | Override job search agent model (default: Groq) |
| `MATCH_MODEL` | No | Override job match agent model (default: Groq) |
| `EMAIL_MODEL` | No | Override email agent model (default: Groq) |
| `LLM_MODEL` | No | Override ALL agents (overridden further by per-agent vars and `--model`) |
| `OLLAMA_BASE_URL` | If using `ollama/` models remotely | Default: `http://localhost:11434` |
| `TOGETHER_API_KEY` | If using `together_ai/` models | — |
| `FIREWORKS_API_KEY` | If using `fireworks_ai/` models | — |
| `OPENROUTER_API_KEY` | If using `openrouter/` models | — |

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
    └─ job_crew.py            ← Crew factory functions
           ├─ crew_agents.py  ← Agent definitions + per-agent LLM routing
           └─ crew_tasks.py   ← Task definitions (description / expected_output)

LinkedIn search/apply also open an MCPServerAdapter context:
    MCPServerAdapter → uvx mcp-server-linkedin → search_jobs / get_job_details tools
```

To add a new agent: create a builder in `crew_agents.py`, a task factory in `crew_tasks.py`, a crew function in `job_crew.py`, and wire a Click command in `main.py`.
