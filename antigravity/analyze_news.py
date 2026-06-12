"""
analyze_news.py
---------------
Finds the latest PDF in /raw_papers/, uploads it to the Gemini Files API,
sends it to gemini-1.5-flash with a finance-focused system prompt, and saves
the Markdown response in /public/digests/digest-YYYY-MM-DD.md.

After processing, the uploaded file is deleted from the Gemini server.
"""

import os
import sys
import glob
import datetime
import pathlib

from google import genai
from google.genai import types

# ── Configuration ─────────────────────────────────────────────────────────────

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("ERROR: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
    sys.exit(1)

MODEL_ID = "gemini-1.5-flash"

SYSTEM_INSTRUCTION = (
    "You are an expert AI Finance Agent. Perform a detailed analytical breakdown "
    "of the provided newspaper. Structure the output in Markdown with these exact sections:\n\n"
    "## 1. Macroeconomic Context & Policy Updates\n"
    "## 2. Equity Markets & Corporate Actions (Highlight stock movements and M&A)\n"
    "## 3. Commodities & Global Trends (Focus specifically on Physical Gold, Silver, and energy)\n"
    "## 4. Academic Application & Financial Concepts (Explain 2-3 complex financial events "
    "from the news using MBA-level theory like Valuation, Arbitrage, or Technical Analysis)."
)

RAW_PAPERS_DIR = pathlib.Path(__file__).parent / "raw_papers"
DIGESTS_DIR = pathlib.Path(__file__).parent / "public" / "digests"

# ── Helpers ───────────────────────────────────────────────────────────────────


def find_latest_pdf() -> pathlib.Path:
    """Return the most recently modified PDF in /raw_papers/."""
    pdfs = sorted(RAW_PAPERS_DIR.glob("*.pdf"), key=os.path.getmtime, reverse=True)
    if not pdfs:
        print("ERROR: No PDF files found in /raw_papers/.", file=sys.stderr)
        sys.exit(1)
    chosen = pdfs[0]
    print(f"[analyze_news] Using PDF: {chosen.name}")
    return chosen


def upload_pdf(client: genai.Client, pdf_path: pathlib.Path) -> types.File:
    """Upload a PDF to the Gemini Files API and wait until it is ACTIVE."""
    print(f"[analyze_news] Uploading {pdf_path.name} to Gemini Files API …")
    uploaded = client.files.upload(
        file=pdf_path,
        config=types.UploadFileConfig(
            mime_type="application/pdf",
            display_name=pdf_path.stem,
        ),
    )

    # Poll until the file is ready (state == ACTIVE)
    import time
    while True:
        file_info = client.files.get(name=uploaded.name)
        if file_info.state == types.FileState.ACTIVE:
            print(f"[analyze_news] File active: {file_info.uri}")
            return file_info
        if file_info.state == types.FileState.FAILED:
            print("ERROR: File processing failed on the Gemini server.", file=sys.stderr)
            sys.exit(1)
        print("[analyze_news] File still processing … waiting 5 s")
        time.sleep(5)


def generate_digest(client: genai.Client, gemini_file: types.File) -> str:
    """Send the uploaded file to gemini-1.5-flash and return the Markdown text."""
    print(f"[analyze_news] Sending file to {MODEL_ID} …")
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri=gemini_file.uri,
                        mime_type="application/pdf",
                    ),
                    types.Part.from_text(
                        text=(
                            "Please perform a full analytical breakdown of this newspaper "
                            "following your system instructions exactly."
                        )
                    ),
                ],
            )
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3,
        ),
    )
    return response.text


def save_digest(markdown_text: str) -> pathlib.Path:
    """Save the digest as digest-YYYY-MM-DD.md in /public/digests/."""
    DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.date.today().isoformat()
    output_path = DIGESTS_DIR / f"digest-{date_str}.md"

    # Prepend a title block so the frontend can display metadata easily
    header = (
        f"---\n"
        f"date: {date_str}\n"
        f"title: Daily Finance Digest — {date_str}\n"
        f"---\n\n"
        f"# Daily Finance Digest — {date_str}\n\n"
    )
    output_path.write_text(header + markdown_text, encoding="utf-8")
    print(f"[analyze_news] Digest saved → {output_path}")
    return output_path


def delete_uploaded_file(client: genai.Client, gemini_file: types.File) -> None:
    """Delete the file from the Gemini Files API to free storage."""
    try:
        client.files.delete(name=gemini_file.name)
        print(f"[analyze_news] Deleted remote file: {gemini_file.name}")
    except Exception as exc:
        # Non-fatal — log and continue
        print(f"[analyze_news] Warning: could not delete remote file: {exc}", file=sys.stderr)


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    client = genai.Client(api_key=API_KEY)

    pdf_path = find_latest_pdf()
    gemini_file = upload_pdf(client, pdf_path)

    try:
        markdown_text = generate_digest(client, gemini_file)
    finally:
        delete_uploaded_file(client, gemini_file)

    save_digest(markdown_text)
    print("[analyze_news] ✅ Done.")


if __name__ == "__main__":
    main()
