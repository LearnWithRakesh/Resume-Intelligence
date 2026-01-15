from __future__ import annotations
import re
from typing import List
from .schemas import AtsReport

def _tok(text: str) -> List[str]:
    return re.findall(r"[A-Za-z][A-Za-z+.#-]*", text.lower())

def keyword_match(resume_text: str, jd_text: str) -> AtsReport:
    resume_tokens = set(_tok(resume_text))
    jd_tokens = set(_tok(jd_text))

    matches = sorted(list(jd_tokens & resume_tokens))[:200]
    missing = sorted(list(jd_tokens - resume_tokens))[:200]

    warnings, suggestions = [], []
    if not resume_text.strip():
        warnings.append("Resume text is empty.")
    if not jd_text.strip():
        warnings.append("JD text is empty; keyword matching disabled.")
    if jd_text.strip() and len(matches) < 15:
        suggestions.append("Low keyword overlap. Add missing keywords where truthful (Skills/Experience).")

    score = (len(matches) / max(len(jd_tokens), 1)) if jd_text.strip() else 0.0
    return AtsReport(
        keyword_matches=matches,
        missing_keywords=missing,
        warnings=warnings,
        suggestions=suggestions,
        score_hint=float(score),
    )
