
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class ResultadoIA:
    id_resultado: UUID
    id_consulta: UUID
    tipo_resultado: str
    conteudo: str
    dados_estruturados: dict[str, Any] = field(default_factory=dict)
    sem_evidencia: bool = False
    modelo_ia: str | None = None
    data_geracao: datetime | None = None
