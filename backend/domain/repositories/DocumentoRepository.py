
from typing import Protocol
from uuid import UUID

from app.domain.entities.documento import Documento
from app.domain.entities.versao_documento import VersaoDocumento


class DocumentoRepository(Protocol):

    def salvar(self, documento: Documento) -> Documento:
        ...

    def buscar_por_id(self, id_documento: UUID) -> Documento | None:
        ...

    def listar(self) -> list[Documento]:
        ...

    def salvar_versao(
        self, versao: VersaoDocumento
    ) -> VersaoDocumento:
        ...

    def buscar_versoes(
        self, id_documento: UUID
    ) -> list[VersaoDocumento]:
        ...
