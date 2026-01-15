from __future__ import annotations
from pathlib import Path
from typing import Union
from pypdf import PdfReader
import docx

def extract_text_from_pdf(path: Union[str, Path]) -> str:
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()

def extract_text_from_docx(path: Union[str, Path]) -> str:
    d = docx.Document(str(path))
    return "\n".join([p.text for p in d.paragraphs]).strip()
