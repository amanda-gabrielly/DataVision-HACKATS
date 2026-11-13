
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Any
from uuid import UUID


@dataclass
class VersaoDocumento:
    id_versao: UUID
    id_documento: UUID
    numero_versao: str
    status_vigencia: str
    inicio_vigencia: date
    fim_vigencia: date | None
    arquivo_path: str
    conteudo_texto: str | None
    extracao_ia: dict[str, Any] = field(default_factory=dict)
    criado_em: datetime | None = None

    def esta_vigente(self, hoje: date) -> bool:
        return (
            self.status_vigencia.lower() == "vigente"
            and self.inicio_vigencia <= hoje
            and (
                self.fim_vigencia is None
                or hoje <= self.fim_vigencia
            )
        )
