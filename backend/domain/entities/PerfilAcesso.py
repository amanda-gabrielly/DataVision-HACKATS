
from dataclasses import dataclass
from uuid import UUID


@dataclass
class PerfilAcesso:
    id_perfil: UUID
    nome: str
    descricao: str | None = None

    def eh_administrador(self) -> bool:
        return self.nome.lower() == "administrador"
