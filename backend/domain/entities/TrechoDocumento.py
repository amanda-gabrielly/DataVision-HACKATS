
from dataclasses import dataclass
from uuid import UUID


@dataclass
class TrechoDocumento:
    id_trecho: UUID
    id_versao: UUID
    conteudo: str
    pagina: int
    ordem: int
    embedding: list[float] | None = None

    def obter_referencia(self) -> str:
        return f"Página {self.pagina}, trecho {self.ordem}"
