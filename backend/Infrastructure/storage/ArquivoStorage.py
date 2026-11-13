
from typing import Protocol


class ArquivoStorage(Protocol):

    async def salvar_arquivo(
        self,
        arquivo,
        caminho: str
    ) -> str:
        ...

    async def obter_arquivo(
        self,
        caminho: str
    ):
        ...
