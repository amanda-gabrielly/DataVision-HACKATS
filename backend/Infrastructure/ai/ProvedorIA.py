
from typing import Protocol


class ProvedorIA(Protocol):

    async def processar(
        self,
        pergunta: str,
        contexto: list
    ) -> dict:
        ...
