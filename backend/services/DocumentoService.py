
from app.domain.entities.documento import Documento
from app.domain.repositories.documento_repository import (
    DocumentoRepository
)


class DocumentoService:

    def __init__(self, repository: DocumentoRepository):
        self.repository = repository

    def cadastrar_documento(
        self,
        documento: Documento
    ) -> Documento:

        documento.titulo = documento.titulo.strip()

        if not documento.titulo:
            raise ValueError("Título obrigatório.")

        return self.repository.salvar(documento)

    def listar_documentos(self):
        return self.repository.listar()
