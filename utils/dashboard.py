"""
utils/dashboard.py — generates an HTML application tracker table.
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime
from typing import List


_BADGE = {
    "Strong":   ("background:#16a34a;color:#fff", "Strong"),
    "Moderate": ("background:#d97706;color:#fff", "Moderate"),
}

_CSS = """\
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:'Inter',sans-serif;font-size:13px;color:#1e293b;background:#f8fafc;padding:32px}
  h1{font-size:22px;font-weight:700;color:#1a365d;margin-bottom:4px}
  .meta{color:#64748b;font-size:12px;margin-bottom:24px}
  table{width:100%;border-collapse:collapse;background:#fff;border-radius:10px;
        overflow:hidden;box-shadow:0 1px 4px rgba(0,0,0,.08)}
  thead{background:#1a365d;color:#fff}
  th{padding:10px 14px;text-align:left;font-weight:600;font-size:12px;
     text-transform:uppercase;letter-spacing:.5px;white-space:nowrap}
  td{padding:10px 14px;border-bottom:1px solid #e2e8f0;vertical-align:top}
  tr:last-child td{border-bottom:none}
  tr:hover td{background:#f1f5f9}
  .rank{font-weight:700;color:#1a365d;font-size:14px;text-align:center}
  .company{font-weight:700;color:#1a365d}
  .title{font-weight:500}
  .location{color:#64748b;font-size:12px}
  .badge{display:inline-block;padding:2px 8px;border-radius:999px;
         font-size:11px;font-weight:600}
  .stack{font-size:11px;color:#475569;line-height:1.5}
  .stack span{display:inline-block;background:#e2e8f0;border-radius:4px;
              padding:1px 6px;margin:1px 2px 1px 0}
  .why{font-size:12px;color:#475569;max-width:280px;line-height:1.4}
  .actions{white-space:nowrap}
  .btn{display:inline-block;padding:4px 10px;border-radius:5px;font-size:12px;
       font-weight:600;text-decoration:none;margin-right:4px;margin-bottom:2px}
  .btn-resume{background:#1a365d;color:#fff}
  .btn-apply{background:#0a66c2;color:#fff}
  .no-pdf{font-size:11px;color:#94a3b8;display:block;margin-top:2px}
  .footer{margin-top:16px;font-size:11px;color:#94a3b8;text-align:center}
</style>"""


def generate_dashboard(
    jobs: List,
    resume_paths: dict,
    output_dir: Path,
    search_meta: dict = None,
) -> Path:
    """
    Generate an HTML dashboard table and write it to output_dir.

    Args:
        jobs: list of MatchedJob instances
        resume_paths: dict keyed by job_id → {"html": Path, "pdf": Path|None}
        output_dir: directory where the dashboard file is written
        search_meta: dict with keys keywords, location, work_type
    Returns:
        Path to the generated dashboard HTML file
    """
    meta = search_meta or {}
    now = datetime.now()
    date_str = now.strftime("%b %d, %Y")
    ts = now.strftime("%Y%m%d_%H%M")

    rows = []
    for job in jobs:
        paths = resume_paths.get(job.job_id, {})
        html_path: Path | None = paths.get("html")
        pdf_path: Path | None = paths.get("pdf")

        # Links are relative — both dashboard and resumes live in output/
        resume_link = ""
        if pdf_path and pdf_path.exists():
            resume_link = (
                f'<a class="btn btn-resume" href="{pdf_path.name}" target="_blank">📄 PDF</a>'
            )
        elif html_path and html_path.exists():
            resume_link = (
                f'<a class="btn btn-resume" href="{html_path.name}" target="_blank">🌐 HTML</a>'
                f'<span class="no-pdf">Print→PDF in Chrome</span>'
            )

        linkedin_url = f"https://www.linkedin.com/jobs/view/{job.job_id}/"
        apply_link = f'<a class="btn btn-apply" href="{linkedin_url}" target="_blank">🔗 Apply</a>'

        badge_style, badge_label = _BADGE.get(job.match_strength, ("background:#e2e8f0;color:#333", job.match_strength))
        badge = f'<span class="badge" style="{badge_style}">{badge_label}</span>'

        stack_chips = "".join(f"<span>{s}</span>" for s in job.stack_overlap)

        rows.append(f"""\
    <tr>
      <td class="rank">{job.rank}</td>
      <td><div class="company">{_esc(job.company)}</div></td>
      <td><div class="title">{_esc(job.title)}</div>
          <div class="location">{_esc(job.location)}</div></td>
      <td>{badge}</td>
      <td><div class="stack">{stack_chips}</div></td>
      <td><div class="why">{_esc(job.why)}</div></td>
      <td class="actions">{resume_link}<br>{apply_link}</td>
    </tr>""")

    keywords_display   = meta.get("keywords", "—")
    location_display   = meta.get("location") or "Worldwide"
    work_type_display  = meta.get("work_type", "any").replace("_", " ").title()
    date_posted_display = meta.get("date_posted", "past_24_hours").replace("_", " ")

    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Job Applications — {date_str}</title>
  {_CSS}
</head>
<body>
  <h1>Job Applications — {date_str}</h1>
  <p class="meta">
    {len(jobs)} match{'es' if len(jobs) != 1 else ''} &nbsp;·&nbsp;
    Keywords: <strong>{_esc(keywords_display)}</strong> &nbsp;·&nbsp;
    Location: <strong>{_esc(location_display)}</strong> &nbsp;·&nbsp;
    Work type: <strong>{work_type_display}</strong> &nbsp;·&nbsp;
    Posted: <strong>{date_posted_display}</strong> &nbsp;·&nbsp;
    Generated {now.strftime("%H:%M")}
  </p>
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Company</th>
        <th>Title / Location</th>
        <th>Match</th>
        <th>Stack overlap</th>
        <th>Why it fits</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
{"".join(rows)}
    </tbody>
  </table>
  <p class="footer">Generated by Job Agent · {now.strftime("%Y-%m-%d %H:%M")}</p>
</body>
</html>"""

    out_path = output_dir / f"applications_{ts}.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def _esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
