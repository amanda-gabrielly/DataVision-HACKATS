
from uuid import UUID

from app.domain.repositories.permissao_documento_repository import (
    PermissaoDocumentoRepository
)


class AutorizacaoService:

    def __init__(
        self,
        permissao_repository: PermissaoDocumentoRepository
    ):
        self.permissao_repository = permissao_repository

    def verificar_acesso(
        self,
        id_usuario: UUID,
        id_perfil: UUID,
        id_documento: UUID,
        acao: str
    ) -> bool:

        permissao = self.permissao_repository.buscar_permissao(
            id_documento=id_documento,
            id_usuario=id_usuario,
            id_perfil=id_perfil
        )

        return permissao is not None and permissao.permissao == acao
