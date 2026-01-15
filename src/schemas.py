from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class JdAnalysis(BaseModel):
    must_have_skills: List[str] = []
    tools_technologies: List[str] = []
    responsibilities: List[str] = []
    domain_terms: List[str] = []
    soft_skills: List[str] = []
    certifications: List[str] = []
    suggested_title: str = ""
    summary_keywords: List[str] = []

class ExperienceItem(BaseModel):
    company: str
    title: str
    location: str = ""
    start: str = Field(..., description="MMM YYYY")
    end: str = Field(..., description="MMM YYYY or Present")
    bullets: List[str]

class ProjectItem(BaseModel):
    name: str
    stack: str
    bullets: List[str]

class ResumeProfile(BaseModel):
    personal_info: Dict[str, Any] = {}
    target_role: str = ""
    years_experience: Optional[float] = None
    country: str = "India"
    skills: List[str] = []
    experience: List[ExperienceItem] = []
    projects: List[ProjectItem] = []
    raw_text_reference: str = ""
    version: str = "v1"

class AtsReport(BaseModel):
    keyword_matches: List[str] = []
    missing_keywords: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []
    score_hint: float = 0.0
