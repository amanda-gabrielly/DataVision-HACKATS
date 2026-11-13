
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class ConsultaDocumento:
    id_consulta_documento: UUID
    id_consulta: UUID
    id_documento: UUID
    id_versao: UUID
    relevancia: Decimal | None = None
