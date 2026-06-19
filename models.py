"""
models.py — Pydantic models for structured CrewAI task output.
"""

from __future__ import annotations
from pydantic import BaseModel
from typing import List


class MatchedJob(BaseModel):
    rank: int
    title: str
    company: str
    location: str
    job_id: str
    match_strength: str          # "Strong" or "Moderate"
    stack_overlap: List[str]
    why: str                     # 1-2 sentence rationale
    jd_text: str                 # condensed JD for resume tailoring (150-250 words)


class SearchResult(BaseModel):
    matched_jobs: List[MatchedJob]
