import io
import os
import random
import re
import time
from typing import Any

import streamlit as st
from google import genai
from google.genai import types
from pypdf import PdfReader
from docx import Document

DEFAULT_MODEL_NAME = "gemini-3.8-flash"
MAX_FILE_SIZE_MB = 5
MAX_RETRIES = 4

st.set_page_config(page_title="Resume ATS Checker", page_icon="📄", layout="wide")


def get_secret(name: str, default: str = "") -> str:
    """Read a setting from Streamlit Secrets first, then environment variables."""
    value = ""
    try:
        value = str(st.secrets.get(name, "") or "").strip()
    except Exception:
        # Streamlit Secrets may not be configured for local development.
        pass
    return value or os.getenv(name, default).strip()


def extract_resume_text(uploaded_file) -> str:
    """Extract readable text from a PDF, DOCX, or TXT resume."""
    file_bytes = uploaded_file.getvalue()
    suffix = uploaded_file.name.lower().rsplit(".", 1)[-1]

    if suffix == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    elif suffix == "docx":
        document = Document(io.BytesIO(file_bytes))
        parts = [paragraph.text for paragraph in document.paragraphs]
        for table in document.tables:
            for row in table.rows:
                parts.append(" | ".join(cell.text for cell in row.cells))
        text = "\n".join(parts)
    elif suffix == "txt":
        text = file_bytes.decode("utf-8", errors="replace")
    else:
        raise ValueError("Unsupported file type. Upload a PDF, DOCX, or TXT file.")

    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        raise ValueError(
            "No readable text was found. If this is a scanned PDF, use a text-based PDF or DOCX instead."
        )
    return text


def estimate_basic_checks(resume_text: str) -> dict[str, Any]:
    """Provide transparent text/section checks; these are not an employer ATS score."""
    text = resume_text.lower()
    words = re.findall(r"\b[\w+#.-]+\b", text)
    section_patterns = {
        "Contact information": r"email|e-mail|phone|mobile|linkedin|github",
        "Experience": r"experience|employment|work history|internship",
        "Education": r"education|university|college|degree|bachelor|master",
        "Skills": r"skills|technical skills|competencies|technologies",
        "Projects": r"projects|personal project|academic project",
    }
    sections = {
        name: bool(re.search(pattern, text))
        for name, pattern in section_patterns.items()
    }
    checks = {
        "Resume has readable text": len(words) >= 50,
        "Contact details appear present": sections["Contact information"],
        "Education section appears present": sections["Education"],
        "Skills section appears present": sections["Skills"],
        "Experience or project section appears present": sections["Experience"] or sections["Projects"],
        "Resume has a reasonable text length": 150 <= len(words) <= 1200,
    }
    return {"word_count": len(words), "sections": sections, "checks": checks}


def make_review_prompt(resume_text: str, job_description: str) -> str:
    job_context = job_description.strip() or (
        "Not provided. Review the resume generally, without assuming a specific job."
    )
    prompt_parts = [
        "You are a careful, practical resume reviewer. Review the supplied resume for ATS readability and job relevance.",
        "Important rules:",
        "- Give an estimated ATS-readiness score from 0 to 100. It is an educational estimate, not a score from a real employer's ATS.",
        "- Do not invent qualifications, experience, metrics, degrees, certifications, or skills.",
        "- Distinguish visible issues from details you cannot verify.",
        "- Be constructive and fair to students and entry-level candidates.",]
