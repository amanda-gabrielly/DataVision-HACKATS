
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from ..base import Base


class DocumentoModel(Base):
    __tablename__ = "documentos"

    id_documento = Column(
        UUID(as_uuid=True),
        primary_key=True
    )

    codigo = Column(String(50), unique=True, nullable=False)
    titulo = Column(String(255), nullable=False)
    tipo = Column(String(50))
    categoria = Column(String(50))
    classificacao = Column(String(20))

    criado_por = Column(UUID(as_uuid=True), nullable=False)

    criado_em = Column(
        DateTime,
        server_default=func.now()
    )
