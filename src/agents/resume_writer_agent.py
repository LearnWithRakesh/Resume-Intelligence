from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from langchain_core.messages import SystemMessage, HumanMessage

from ..config import Settings
from ..llm import make_chat_llm
from ..schemas import ResumeProfile, JdAnalysis

PROMPTS = Path(__file__).resolve().parents[1] / "prompts"


def generate_resume_draft(
    settings: Settings, profile: ResumeProfile, jd: Optional[JdAnalysis] = None
) -> Dict[str, Any]:
    system = (PROMPTS / "system_resume_writer.md").read_text(encoding="utf-8")
    instr = (PROMPTS / "resume_rewrite_from_profile.md").read_text(encoding="utf-8")

    llm = make_chat_llm(settings, temperature=0.2)
    payload = {"resume_profile": profile.model_dump(), "jd_analysis": jd.model_dump() if jd else None}

    msg = [
        SystemMessage(content=system),
        HumanMessage(content=f"{instr}\n\nINPUT_JSON:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"),
    ]
    out = llm.invoke(msg).content

    try:
        return json.loads(out)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Resume Writer returned invalid JSON: {e}\nRaw:\n{out}")
