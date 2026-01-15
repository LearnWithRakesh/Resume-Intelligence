from __future__ import annotations

import json
import os
import streamlit as st

from src.config import load_settings
from src.parsers.extract_text import extract_text_from_pdf, extract_text_from_docx
from src.agents.jd_analyzer import analyze_jd
from src.agents.resume_parser_agent import parse_resume_text
from src.agents.resume_writer_agent import generate_resume_draft
from src.ats import keyword_match
from src.rag.store import chunk_text, index_documents, retrieve
from src.rag.personalize import personalize_with_rag


st.set_page_config(page_title="IT Resume Intelligence", page_icon="🧾", layout="wide")
st.title("IT Resume Intelligence (MVP)")
st.caption("Resume/notes + JD → structured profile + ATS report + RAG personalization + resume draft.")

with st.sidebar:
    page = st.radio("Go to", ["Intake", "JD Analyzer", "ATS Report", "RAG Personalize", "Resume Draft"], index=0)
    st.divider()
   # st.info("Set OPENAI_API_KEY in .env (local) or Streamlit Secrets (deploy).")


def _ensure_upload_dir():
    os.makedirs("data/samples", exist_ok=True)


def load_resume_text():
    st.subheader("Resume / Notes Input")
    mode = st.radio("Input type", ["Paste Text", "Upload PDF", "Upload DOCX"], horizontal=True)
    _ensure_upload_dir()

    if mode == "Paste Text":
        return st.text_area("Paste resume or notes", height=240).strip()

    if mode == "Upload PDF":
        f = st.file_uploader("Upload PDF", type=["pdf"])
        if not f:
            return ""
        path = f"data/samples/_upload_{f.name}"
        with open(path, "wb") as out:
            out.write(f.getbuffer())
        return extract_text_from_pdf(path)

    if mode == "Upload DOCX":
        f = st.file_uploader("Upload DOCX", type=["docx"])
        if not f:
            return ""
        path = f"data/samples/_upload_{f.name}"
        with open(path, "wb") as out:
            out.write(f.getbuffer())
        return extract_text_from_docx(path)

    return ""


# Session state
st.session_state.setdefault("resume_text", "")
st.session_state.setdefault("jd_text", "")
st.session_state.setdefault("profile", None)
st.session_state.setdefault("jd_analysis", None)
st.session_state.setdefault("draft", None)


if page == "Intake":
    st.session_state["resume_text"] = load_resume_text()
    st.session_state["jd_text"] = st.text_area("Paste Job Description (recommended)", value=st.session_state["jd_text"], height=180)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Structure Resume (LangChain)", type="primary"):
            if not st.session_state["resume_text"]:
                st.error("Please provide resume text/notes first.")
            else:
                settings = load_settings()
                profile = parse_resume_text(settings, st.session_state["resume_text"])
                st.session_state["profile"] = profile.model_dump()
                st.success("Structured profile created.")
                st.json(st.session_state["profile"])

    with col2:
        if st.button("Analyze JD"):
            if not st.session_state["jd_text"].strip():
                st.error("Paste JD text first.")
            else:
                settings = load_settings()
                jd = analyze_jd(settings, st.session_state["jd_text"])
                st.session_state["jd_analysis"] = jd.model_dump()
                st.success("JD analysis created.")
                st.json(st.session_state["jd_analysis"])


elif page == "JD Analyzer":
    st.subheader("JD Analyzer")
    if st.session_state["jd_analysis"] is None:
        st.info("Go to Intake → Analyze JD.")
    else:
        st.json(st.session_state["jd_analysis"])
        st.download_button("Download JD JSON", json.dumps(st.session_state["jd_analysis"], indent=2), "jd_analysis.json")


elif page == "ATS Report":
    st.subheader("ATS Keyword Match")
    resume_text = st.session_state["resume_text"]
    jd_text = st.session_state["jd_text"]

    if not resume_text.strip():
        st.info("Provide resume text in Intake.")
    else:
        report = keyword_match(resume_text, jd_text)
        st.write(f"Overlap Score (heuristic): **{report.score_hint:.2f}**")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### Present")
            st.write(report.keyword_matches[:80])
        with c2:
            st.markdown("### Missing")
            st.write(report.missing_keywords[:80])
        if report.warnings:
            st.warning("\n".join(report.warnings))
        if report.suggestions:
            st.info("\n".join(report.suggestions))


elif page == "RAG Personalize":
    st.subheader("RAG Personalize")
    if st.button("Build/Update Resume Index"):
        if not st.session_state["resume_text"].strip():
            st.error("Provide resume text in Intake first.")
        else:
            settings = load_settings()
            docs = chunk_text(st.session_state["resume_text"], source="resume")
            index_documents(settings, "resume_corpus", docs)
            st.success("Resume indexed.")

    query = st.text_input("Query (leave empty to use JD)", value="")
    if st.button("Retrieve & Personalize"):
        settings = load_settings()
        q = query.strip() or st.session_state["jd_text"].strip()
        if not q:
            st.error("Provide JD or query.")
        else:
            hits = retrieve(settings, "resume_corpus", q, k=6)
            chunks = [h.page_content for h in hits]
            st.markdown("### Retrieved Chunks")
            for i, ch in enumerate(chunks, 1):
                with st.expander(f"Chunk {i}"):
                    st.write(ch)

            if st.session_state["jd_text"].strip():
                out = personalize_with_rag(settings, st.session_state["jd_text"], chunks)
                st.markdown("### Personalization Output")
                st.json(out)
            else:
                st.info("Paste JD for personalization suggestions; retrieval works without JD.")


elif page == "Resume Draft":
    st.subheader("Generate Resume Draft")
    if st.session_state["profile"] is None:
        st.info("Go to Intake → Structure Resume.")
    else:
        if st.button("Generate Draft", type="primary"):
            settings = load_settings()
            from src.schemas import ResumeProfile, JdAnalysis
            profile = ResumeProfile.model_validate(st.session_state["profile"])
            jd = JdAnalysis.model_validate(st.session_state["jd_analysis"]) if st.session_state["jd_analysis"] else None
            draft = generate_resume_draft(settings, profile, jd)
            st.session_state["draft"] = draft

        if st.session_state["draft"]:
            draft = st.session_state["draft"]
            st.json(draft)

            # ATS text
            lines = []
            lines.append(draft.get("headline",""))
            lines.append("")
            lines.append("SUMMARY")
            lines.append(draft.get("summary",""))
            lines.append("")
            lines.append("SKILLS")
            for s in draft.get("skills", []):
                lines.append(f"- {s}")
            lines.append("")
            lines.append("EXPERIENCE")
            for exp in draft.get("experience", []):
                lines.append(f"{exp.get('title','')} | {exp.get('company','')} | {exp.get('location','')} | {exp.get('start','')} - {exp.get('end','')}")
                for b in exp.get("bullets", []):
                    lines.append(f"  - {b}")
                lines.append("")
            lines.append("PROJECTS")
            for p in draft.get("projects", []):
                lines.append(f"{p.get('name','')} | {p.get('stack','')}")
                for b in p.get("bullets", []):
                    lines.append(f"  - {b}")
                lines.append("")

            st.markdown("### ATS-friendly Text")
            st.text("\n".join(lines))

            st.download_button("Download Draft JSON", json.dumps(draft, indent=2), "resume_draft.json")
            st.download_button("Download ATS Text", "\n".join(lines), "resume_draft.txt")
