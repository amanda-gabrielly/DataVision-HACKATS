
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Usuario:
    id_usuario: UUID
    id_perfil: UUID
    nome: str
    email: str
    cargo: str
    setor: str
    status: str
    criado_em: datetime

    def esta_ativo(self) -> bool:
        return self.status.lower() == "ativo"
