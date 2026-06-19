"""
utils/file_utils.py — helpers for reading JDs and saving output.
"""

import os
import re
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def read_jd(path: str) -> str:
    """Read a job description from a text file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def slugify(text: str) -> str:
    """Turn a company name or title into a safe filename slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    return text[:40]


def save_output(content: str, prefix: str, company: str = "", ext: str = "html") -> Path:
    """Save generated content to the output directory."""
    date = datetime.now().strftime("%Y%m%d")
    company_slug = f"_{slugify(company)}" if company else ""
    filename = f"{prefix}{company_slug}_{date}.{ext}"
    path = OUTPUT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
