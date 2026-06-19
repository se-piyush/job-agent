"""
utils/pdf_utils.py — converts HTML resume files to PDF via Playwright.

Playwright is an optional dependency. If not installed, this module degrades
gracefully: html_to_pdf() returns None and callers fall back to HTML-only.

One-time setup (after pip install playwright):
    playwright install chromium
"""

from __future__ import annotations
from pathlib import Path


def html_string_to_pdf(html: str, pdf_path: Path) -> Path | None:
    """
    Convert an HTML string directly to PDF without leaving an HTML file on disk.
    Writes to a temp file, converts via Playwright, then deletes the temp file.

    Returns pdf_path on success, or None if playwright is unavailable or conversion fails.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False,
                                     mode="w", encoding="utf-8") as f:
        f.write(html)
        tmp = Path(f.name)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(tmp.as_uri(), wait_until="networkidle")
            page.emulate_media(media="print")
            page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
            browser.close()
        return pdf_path
    except Exception:
        return None
    finally:
        tmp.unlink(missing_ok=True)


def html_to_pdf(html_path: Path) -> Path | None:
    """
    Convert an HTML file to PDF using a headless Chromium browser.
    Replicates Chrome's "Print → Save as PDF → No margins" behaviour.

    Returns the PDF Path on success, or None if playwright is unavailable
    or the conversion fails.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    pdf_path = html_path.with_suffix(".pdf")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            # Use file URI so relative font/asset links resolve correctly
            page.goto(html_path.as_uri(), wait_until="networkidle")
            page.emulate_media(media="print")
            page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
            browser.close()
        return pdf_path
    except Exception:
        return None


def is_available() -> bool:
    """Returns True if playwright + chromium are installed and usable."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            browser.close()
        return True
    except Exception:
        return False
