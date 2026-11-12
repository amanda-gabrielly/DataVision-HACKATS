import os
import re
from collections import Counter
from contextlib import asynccontextmanager
from datetime import datetime
from io import BytesIO

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pypdf import PdfReader
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    func,
    select,
)
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


database_url = URL.create(
    "postgresql+psycopg",
    username="postgres",
    password=os.getenv("POSTGRES_PASSWORD", ""),
    host="localhost",
    port=5432,
    database="datavision",
)

engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="Geral")
    version: Mapped[str] = mapped_column(String(40), default="Não identificada")
    pages: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
    )
    page: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    document: Mapped[Document] = relationship(back_populates="chunks")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="DataVision BBTS API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def split_text(text: str, size: int = 950, overlap: int = 100) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    result = []
    start = 0

    while start < len(text):
        end = min(start + size, len(text))

        if end < len(text):
            boundary = text.rfind(" ", start + size // 2, end)
            if boundary > start:
                end = boundary

        result.append(text[start:end])

        if end == len(text):
            break

        start = max(start + 1, end - overlap)

    return result


def words(text: str) -> list[str]:
    return [
        word
        for word in re.findall(r"[a-z0-9áàâãéêíóôõúç]+", text.lower())
        if len(word) > 2
    ]


def document_json(document: Document) -> dict:
    return {
        "id": document.id,
        "title": document.title,
        "category": document.category,
        "version": document.version,
        "pages": document.pages,
    }


class Question(BaseModel):
    question: str = Field(min_length=5, max_length=1000)


@app.get("/")
def home():
    return {"status": "DataVision backend online"}


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ok", "database": "connected"}


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    documents = db.scalars(
        select(Document).order_by(Document.created_at.desc())
    ).all()

    categories = Counter(document.category for document in documents)

    return {
        "documents": len(documents),
        "topics": len(categories),
        "chunks": db.scalar(select(func.count(DocumentChunk.id))) or 0,
        "categories": [
            {"name": name, "count": count}
            for name, count in categories.items()
        ],
    }


@app.get("/api/documents")
def list_documents(db: Session = Depends(get_db)):
    documents = db.scalars(
        select(Document).order_by(Document.created_at.desc())
    ).all()

    return [document_json(document) for document in documents]


@app.post("/api/documents")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("Geral"),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF.")

    content = await file.read()

    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="O limite por arquivo é 20 MB.")

    try:
        reader = PdfReader(BytesIO(content))
        pages = [
            (page_number, page.extract_text() or "")
            for page_number, page in enumerate(reader.pages, start=1)
        ]
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível ler este PDF.",
        ) from error

    if not any(text.strip() for _, text in pages):
        raise HTTPException(
            status_code=422,
            detail="Este PDF não tem texto selecionável.",
        )

    title = os.path.basename(file.filename.replace("\\", "/"))[:240]
    version_match = re.search(r"v[ _-]?(\d+(?:\.\d+)*)", title, re.IGNORECASE)

    document = Document(
        title=title,
        category=category.strip()[:80] or "Geral",
        version=version_match.group(1) if version_match else "Não identificada",
        pages=len(reader.pages),
    )

    for page_number, text in pages:
        for chunk in split_text(text):
            document.chunks.append(
                DocumentChunk(page=page_number, content=chunk)
            )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document_json(document) | {"indexed_chunks": len(document.chunks)}


@app.post("/api/ask")
def ask_question(payload: Question, db: Session = Depends(get_db)):
    query_words = set(words(payload.question))

    if not query_words:
        raise HTTPException(
            status_code=422,
            detail="Inclua palavras mais específicas na pergunta.",
        )

    rows = db.execute(
        select(DocumentChunk, Document).join(Document)
    ).all()

    ranked = []

    for chunk, document in rows:
        counts = Counter(words(chunk.content))
        matches = query_words.intersection(counts)

        if matches:
            score = len(matches) / len(query_words)
            ranked.append((score, chunk, document))

    ranked.sort(key=lambda item: item[0], reverse=True)
    best_matches = ranked[:4]

    if not best_matches:
        return {
            "answer": "Não encontrei evidências suficientes nos documentos. Tente reformular a pergunta ou envie uma fonte relevante.",
            "citations": [],
            "needs_review": True,
        }

    citations = [
        {
            "document": document.title,
            "version": document.version,
            "category": document.category,
            "page": chunk.page,
            "excerpt": chunk.content,
        }
        for _, chunk, document in best_matches
    ]

    score, chunk, document = best_matches[0]

    return {
        "answer": (
            f"Encontrei trechos relacionados. A evidência mais relevante está em "
            f"{document.title}, página {chunk.page}: {chunk.content}"
        ),
        "citations": citations,
        "needs_review": score < 0.2,
    }