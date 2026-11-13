
from sqlalchemy import Column, String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from ..base import Base


class DocumentoModel(Base):
    __tablename__ = "documentos"

    id_documento = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    codigo = Column(String(50), unique=True, nullable=False)
    titulo = Column(String(255), nullable=False)
    tipo = Column(String(50), nullable=True)
    categoria = Column(String(50), nullable=False)
    classificacao = Column(String(20), nullable=False)

    criado_por = Column(UUID(as_uuid=True), nullable=True)

    criado_em = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
