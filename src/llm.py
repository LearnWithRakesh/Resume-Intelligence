from __future__ import annotations
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from .config import Settings

def make_chat_llm(settings: Settings, temperature: float = 0.2) -> ChatOpenAI:
    return ChatOpenAI(model=settings.openai_model, temperature=temperature, api_key=settings.openai_api_key)

def make_embeddings(settings: Settings) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=settings.openai_embeddings_model, api_key=settings.openai_api_key)
