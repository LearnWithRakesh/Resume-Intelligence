from __future__ import annotations

from dataclasses import dataclass
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from ..config import Settings
from ..llm import make_embeddings


@dataclass(frozen=True)
class IndexedCorpus:
    vectordb: Chroma
    collection_name: str


def chunk_text(text: str, source: str, chunk_size: int = 900, chunk_overlap: int = 120) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(text)
    return [Document(page_content=c, metadata={"source": source}) for c in chunks]


def build_or_load(settings: Settings, collection_name: str) -> Chroma:
    emb = make_embeddings(settings)
    return Chroma(
        collection_name=collection_name,
        embedding_function=emb,
        persist_directory=settings.chroma_dir,
    )


def index_documents(settings: Settings, collection_name: str, docs: List[Document]) -> IndexedCorpus:
    db = build_or_load(settings, collection_name)
    db.add_documents(docs)
    db.persist()
    return IndexedCorpus(vectordb=db, collection_name=collection_name)


def retrieve(settings: Settings, collection_name: str, query: str, k: int = 6) -> List[Document]:
    db = build_or_load(settings, collection_name)
    return db.similarity_search(query, k=k)
