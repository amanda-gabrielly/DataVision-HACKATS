
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class LogAcesso:
    id_log: UUID
    id_usuario: UUID
    acao: str
    data_hora: datetime
    ip: str | None = None
