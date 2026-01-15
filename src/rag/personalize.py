from __future__ import annotations

import json
from typing import Dict, Any, List

from langchain_core.messages import SystemMessage, HumanMessage

from ..config import Settings
from ..llm import make_chat_llm


PERSONALIZE_SYSTEM = """You are an expert IT Resume Writer and ATS specialist.
You will be provided:
1) Job Description (JD)
2) Retrieved relevant resume chunks (from candidate's resume)

Task:
- Propose targeted improvements ONLY for the retrieved chunks, aligned to JD keywords.
- Do NOT invent new employers, dates, tools, or metrics.
- If metrics are missing, use placeholders like [X%], [N], [hrs], [₹].

Return ONLY JSON:
{
  "updated_bullets": ["..."],
  "keywords_to_add": ["..."],
  "risks_or_gaps": ["..."]
}
"""


def personalize_with_rag(settings: Settings, jd_text: str, retrieved_chunks: List[str]) -> Dict[str, Any]:
    llm = make_chat_llm(settings, temperature=0.2)
    payload = {"jd": jd_text, "retrieved_chunks": retrieved_chunks}
    msg = [SystemMessage(content=PERSONALIZE_SYSTEM), HumanMessage(content=json.dumps(payload, ensure_ascii=False))]
    out = llm.invoke(msg).content
    try:
        return json.loads(out)
    except Exception as e:
        return {"updated_bullets": [], "keywords_to_add": [], "risks_or_gaps": [f"Parse error: {e}"]}
