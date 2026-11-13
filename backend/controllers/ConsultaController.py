
from fastapi import APIRouter

router = APIRouter(prefix="/consultas", tags=["Consultas"])


@router.post("/")
async def enviar_pergunta(dados: dict):
    # Validar os dados com Pydantic.
    # Chamar ConsultaService.
    pass


@router.get("/{id_consulta}")
async def obter_consulta(id_consulta: str):
    # Consultar histórico e resultado.
    pass
