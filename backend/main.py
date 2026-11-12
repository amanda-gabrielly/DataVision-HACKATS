import hashlib
import os
import re
from collections import Counter
from contextlib import asynccontextmanager
from datetime import date, datetime
from io import BytesIO
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pypdf import PdfReader
from sqlalchemy import (
    BigInteger,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
    func,
    select,
    text,
)
from sqlalchemy.engine import URL
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

MAX_FILE_BYTES = 20 * 1024 * 1024
MIGRATION_FILE = Path(__file__).parent / "migrations" / "001_document_processing.sql"

shared_database_url = os.getenv("DATABASE_URL")
if shared_database_url:
    if shared_database_url.startswith("postgres://"):
        shared_database_url = shared_database_url.replace(
            "postgres://", "postgresql+psycopg://", 1
        )
    elif shared_database_url.startswith("postgresql://"):
        shared_database_url = shared_database_url.replace(
            "postgresql://", "postgresql+psycopg://", 1
        )
    engine = create_engine(shared_database_url, pool_pre_ping=True)
else:
    local_database_url = URL.create(
        "postgresql+psycopg",
        username="postgres",
        password=os.getenv("POSTGRES_PASSWORD", ""),
        host="localhost",
        port=5432,
        database="datavision",
    )
    engine = create_engine(local_database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="Geral")
    area: Mapped[str] = mapped_column(
        String(120), default="Geral", server_default="Geral", nullable=False
    )
    topic: Mapped[str] = mapped_column(
        String(120), default="Geral", server_default="Geral", nullable=False
    )
    document_type: Mapped[str] = mapped_column(
        String(80), default="Outro", server_default="Outro", nullable=False
    )
    version: Mapped[str] = mapped_column(
        String(40), default="Não identificada", server_default="Não identificada"
    )
    document_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    source_filename: Mapped[str | None] = mapped_column(String(240), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
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


def apply_schema():
    with engine.begin() as connection:
        # Prevent simultaneous app starts from applying the migration together.
        connection.execute(text("SELECT pg_advisory_xact_lock(74120918)"))
        Base.metadata.create_all(bind=connection)

        if MIGRATION_FILE.exists():
            migration_sql = MIGRATION_FILE.read_text(encoding="utf-8")
            for statement in migration_sql.split(";"):
                if statement.strip():
                    connection.execute(text(statement))


@asynccontextmanager
async def lifespan(app: FastAPI):
    apply_schema()
    yield


app = FastAPI(title="DataVision BBTS API", version="0.2.0", lifespan=lifespan)

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


def split_text(content: str, size: int = 950, overlap: int = 100) -> list[str]:
    content = re.sub(r"\s+", " ", content).strip()
    result = []
    start = 0

    while start < len(content):
        end = min(start + size, len(content))

        if end < len(content):
            boundary = content.rfind(" ", start + size // 2, end)
            if boundary > start:
                end = boundary

        result.append(content[start:end])

        if end == len(content):
            break

        start = max(start + 1, end - overlap)

    return result


def words(content: str) -> list[str]:
    return [
        word
        for word in re.findall(r"[a-z0-9áàâãéêíóôõúç]+", content.lower())
        if len(word) > 2
    ]


def safe_filename(filename: str) -> str:
    return os.path.basename(filename.replace("\\", "/"))[:240]


def extract_version(filename: str) -> str:
    match = re.search(
        r"(?:^|[\s_.-])v[\s_-]?(\d+(?:\.\d+)*)",
        filename,
        re.IGNORECASE,
    )
    return match.group(1) if match else "Não identificada"


def extract_date(filename: str) -> date | None:
    patterns = (
        (r"(?<!\d)(20\d{2})[._-](\d{1,2})[._-](\d{1,2})(?!\d)", "ymd"),
        (r"(?<!\d)(\d{1,2})[._-](\d{1,2})[._-](20\d{2})(?!\d)", "dmy"),
    )

    for pattern, order in patterns:
        match = re.search(pattern, filename)
        if not match:
            continue
        try:
            if order == "ymd":
                year, month, day = map(int, match.groups())
            else:
                day, month, year = map(int, match.groups())
            return date(year, month, day)
        except ValueError:
            continue

    return None


def document_json(document: Document) -> dict:
    return {
        "id": document.id,
        "title": document.title,
        "source_filename": document.source_filename,
        "category": document.category,
        "area": document.area,
        "topic": document.topic,
        "document_type": document.document_type,
        "version": document.version,
        "document_date": (
            document.document_date.isoformat() if document.document_date else None
        ),
        "file_size": document.file_size,
        "pages": document.pages,
    }

def get_existing_hash(db: Session, content_hash: str) -> Document | None:
    return db.scalar(
        select(Document).where(Document.content_hash == content_hash)
    )


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
    topics = Counter(document.topic for document in documents)

    return {
        "documents": len(documents),
        "topics": len(topics),
        "chunks": db.scalar(select(func.count(DocumentChunk.id))) or 0,
        "categories": [
            {"name": name, "count": count}
            for name, count in topics.items()
        ],
    }


@app.get("/api/documents")
def list_documents(db: Session = Depends(get_db)):
    documents = db.scalars(
        select(Document).order_by(Document.created_at.desc())
    ).all()
    return [document_json(document) for document in documents]


async def save_pdf(
    *,
    file: UploadFile,
    area: str,
    topic: str,
    document_type: str,
    document_date: str | None,
    db: Session,
) -> dict:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF.")

    content = await file.read()
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="O limite por arquivo é 20 MB.",
        )

    source_filename = safe_filename(file.filename)
    content_hash = hashlib.sha256(content).hexdigest()

    existing = get_existing_hash(db, content_hash)
    if existing:
        return {
            "duplicate": True,
            "message": "Este mesmo arquivo já está no acervo.",
            "document": document_json(existing),
        }

    try:
        reader = PdfReader(BytesIO(content))
        extracted_pages = [
            (page_number, page.extract_text() or "")
            for page_number, page in enumerate(reader.pages, start=1)
        ]
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível ler este PDF.",
        ) from error

    searchable_pages = [
        (page_number, page_text)
        for page_number, page_text in extracted_pages
        if page_text.strip()
    ]

    if not searchable_pages:
        raise HTTPException(
            status_code=422,
            detail=(
                "Este PDF não contém texto selecionável. "
                "Parece digitalizado; OCR ainda não está ativo."
            ),
        )

    metadata = reader.metadata
    metadata_title = str(metadata.title).strip() if metadata and metadata.title else ""
    title = (metadata_title or Path(source_filename).stem).strip()[:240]

    version = extract_version(source_filename)
    if version == "Não identificada":
        version = extract_version(title)

    metadata_date = None
    if metadata:
        for field_name in ("creation_date", "modification_date"):
            metadata_value = getattr(metadata, field_name, None)
            if isinstance(metadata_value, datetime):
                metadata_date = metadata_value.date()
                break

    if document_date:
        try:
            resolved_date = date.fromisoformat(document_date)
        except ValueError as error:
            raise HTTPException(
                status_code=422,
                detail="A data deve estar no formato AAAA-MM-DD.",
            ) from error
    else:
        resolved_date = (
            extract_date(source_filename)
            or extract_date(title)
            or metadata_date
        )

    normalized_area = area.strip()[:120] or "Geral"
    normalized_topic = topic.strip()[:120] or "Geral"
    normalized_type = document_type.strip()[:80] or "Outro"

    document = Document(
        title=title,
        source_filename=source_filename,
        category=normalized_topic[:80],
        area=normalized_area,
        topic=normalized_topic,
        document_type=normalized_type,
        version=version,
        document_date=resolved_date,
        content_hash=content_hash,
        file_size=len(content),
        pages=len(reader.pages),
    )

    for page_number, page_text in searchable_pages:
        for chunk in split_text(page_text):
            document.chunks.append(
                DocumentChunk(page=page_number, content=chunk)
            )

    db.add(document)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = get_existing_hash(db, content_hash)
        if existing:
            return {
                "duplicate": True,
                "message": "Este mesmo arquivo já foi enviado por outra pessoa.",
                "document": document_json(existing),
            }
        raise

    db.refresh(document)
    empty_pages = len(extracted_pages) - len(searchable_pages)

    return {
        "duplicate": False,
        "message": "PDF processado e indexado.",
        "document": document_json(document),
        "indexed_chunks": len(document.chunks),
        "warning": (
            f"{empty_pages} página(s) sem texto selecionável não foram indexadas."
            if empty_pages
            else None
        ),
    }


@app.post("/api/documents")
async def upload_document(
    file: UploadFile = File(...),
    area: str = Form("Geral"),
    topic: str = Form("Geral"),
    document_type: str = Form("Outro"),
    document_date: str | None = Form(None),
    db: Session = Depends(get_db),
):
    return await save_pdf(
        file=file,
        area=area,
        topic=topic,
        document_type=document_type,
        document_date=document_date,
        db=db,
    )


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
            "source_filename": document.source_filename,
            "version": document.version,
            "category": document.category,
            "area": document.area,
            "topic": document.topic,
            "document_type": document.document_type,
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
