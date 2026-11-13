
from sqlalchemy.orm import Session

from backend.Infrastructure.database.models.DocumentoModel import DocumentoModel


class PostgresDocumentoRepository:

    def __init__(self, db: Session):
        self.db = db

    def buscar_por_id(self, id_documento):
        return (
            self.db.query(DocumentoModel)
            .filter(
                DocumentoModel.id_documento == id_documento
            )
            .first()
        )

    def listar(self):
        return self.db.query(DocumentoModel).all()
