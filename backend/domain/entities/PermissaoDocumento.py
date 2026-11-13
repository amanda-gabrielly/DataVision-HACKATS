
from dataclasses import dataclass
from uuid import UUID


@dataclass
class PermissaoDocumento:
    id_permissao: UUID
    id_documento: UUID
    permissao: str
    id_perfil: UUID | None = None
    id_usuario: UUID | None = None

    def __post_init__(self):
        if (self.id_perfil is None) == (self.id_usuario is None):
            raise ValueError(
                "Informe exatamente um perfil ou usuário."
            )
