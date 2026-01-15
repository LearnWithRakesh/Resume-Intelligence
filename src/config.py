from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_embeddings_model: str = "text-embedding-3-small"
    app_env: str = "dev"
    chroma_dir: str = "chroma_db"

def load_settings() -> Settings:
    load_dotenv(override=False)

    secrets = {}
    try:
        import streamlit as st  # type: ignore
        secrets = dict(st.secrets) if hasattr(st, "secrets") else {}
    except Exception:
        secrets = {}

    def pick(key: str, default: str | None = None) -> str | None:
        return secrets.get(key) or os.getenv(key) or default

    api_key = pick("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing. Set in .env (local) or Streamlit Secrets (deploy).")

    return Settings(
        openai_api_key=api_key,
        openai_model=pick("OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini",
        openai_embeddings_model=pick("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")
        or "text-embedding-3-small",
        app_env=pick("APP_ENV", "dev") or "dev",
        chroma_dir=pick("CHROMA_DIR", "chroma_db") or "chroma_db",
    )
