# IT Resume Intelligence (Streamlit + OpenAI + LangChain RAG)

A **product-grade MVP** for an AI-powered resume intelligence platform focused on **IT professionals**.

## What you can do (MVP)
- Create from scratch (structured form via JSON input)
- Paste existing resume/notes and **structure** it using LangChain (Resume Parser Agent)
- Paste a JD and extract ATS buckets (JD Analyzer Agent)
- ATS report: present/missing keywords + suggestions
- RAG: chunk/index resume, retrieve relevant chunks for JD, propose targeted improvements
- Generate an ATS-friendly resume draft (JSON + plain text)

## Run locally

python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# set OPENAI_API_KEY in .env

streamlit run app/streamlit_app.py


## Deploy (Streamlit Community Cloud)
- Push this repo to GitHub
- In Streamlit Cloud → New app → main file: `app/streamlit_app.py`
- Add secrets:

OPENAI_API_KEY="..."
OPENAI_MODEL="gpt-4o-mini"
OPENAI_EMBEDDINGS_MODEL="text-embedding-3-small"


## Notebooks
Use `notebooks/` for prompt/agent experiments, then move stable logic into `src/`.

## Safety
- Keys are in `.env` (local) or Streamlit Secrets (prod)
- No fabrication: placeholders for missing metrics ([X%], [N], [hrs], [₹]) + risks list

# Resume-Intelligence
