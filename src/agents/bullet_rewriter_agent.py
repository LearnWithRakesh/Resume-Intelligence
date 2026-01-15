from __future__ import annotations

import json
from pathlib import Path
from typing import List

from langchain_core.messages import SystemMessage, HumanMessage

from ..config import Settings
from ..llm import make_chat_llm

PROMPTS = Path(__file__).resolve().parents[1] / "prompts"


def rewrite_bullets(settings: Settings, bullets: List[str], role_context: str = "") -> List[str]:
    system = (PROMPTS / "system_resume_writer.md").read_text(encoding="utf-8")
    instr = (PROMPTS / "bullet_rewriter.md").read_text(encoding="utf-8")

    llm = make_chat_llm(settings, temperature=0.2)
    payload = {"role_context": role_context, "bullets": bullets}
    msg = [
        SystemMessage(content=system),
        HumanMessage(content=f"{instr}\n\nINPUT_JSON:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"),
    ]
    out = llm.invoke(msg).content

    try:
        data = json.loads(out)
        return data.get("bullets", bullets)
    except Exception:
        return bullets
