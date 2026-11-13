
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class Fonte:
    id_fonte: UUID
    id_resultado: UUID
    id_consulta_documento: UUID
    id_trecho: UUID
    id_versao: UUID
    citacao: str
    pagina: int
    confianca: Decimal | None = None
