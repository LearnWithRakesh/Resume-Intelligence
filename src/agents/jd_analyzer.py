from __future__ import annotations

import json
from pathlib import Path

from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import ValidationError

from ..config import Settings
from ..llm import make_chat_llm
from ..schemas import JdAnalysis

PROMPTS = Path(__file__).resolve().parents[1] / "prompts"


def analyze_jd(settings: Settings, jd_text: str) -> JdAnalysis:
    system = (PROMPTS / "system_resume_writer.md").read_text(encoding="utf-8")
    instr = (PROMPTS / "jd_analyzer.md").read_text(encoding="utf-8")

    llm = make_chat_llm(settings, temperature=0.1)
    msg = [
        SystemMessage(content=system),
        HumanMessage(content=f"{instr}\n\nJOB_DESCRIPTION:\n{jd_text}"),
    ]
    out = llm.invoke(msg).content

    try:
        data = json.loads(out)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JD Analyzer returned invalid JSON: {e}\nRaw:\n{out}")

    try:
        return JdAnalysis.model_validate(data)
    except ValidationError as e:
        raise RuntimeError(f"JD Analyzer JSON schema mismatch: {e}\nParsed:\n{json.dumps(data, indent=2)}")
