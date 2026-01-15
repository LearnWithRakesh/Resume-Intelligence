from __future__ import annotations

import json
from pathlib import Path

from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import ValidationError

from ..config import Settings
from ..llm import make_chat_llm
from ..schemas import ResumeProfile

PROMPTS = Path(__file__).resolve().parents[1] / "prompts"


def parse_resume_text(settings: Settings, raw_text: str) -> ResumeProfile:
    system = (PROMPTS / "system_resume_writer.md").read_text(encoding="utf-8")
    instr = (PROMPTS / "resume_parser.md").read_text(encoding="utf-8")

    llm = make_chat_llm(settings, temperature=0.1)
    msg = [
        SystemMessage(content=system),
        HumanMessage(content=f"{instr}\n\nRAW_RESUME_TEXT:\n{raw_text}"),
    ]
    out = llm.invoke(msg).content

    try:
        data = json.loads(out)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Resume Parser returned invalid JSON: {e}\nRaw:\n{out}")

    data["raw_text_reference"] = raw_text[:5000]
    data.setdefault("version", "v1")

    try:
        return ResumeProfile.model_validate(data)
    except ValidationError as e:
        raise RuntimeError(f"Resume Parser JSON schema mismatch: {e}\nParsed:\n{json.dumps(data, indent=2)}")
