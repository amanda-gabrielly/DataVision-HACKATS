
from fastapi import APIRouter, UploadFile, File, Depends

router = APIRouter(prefix="/documentos", tags=["Documentos"])


@router.post("/upload")
async def upload_documento(
    arquivo: UploadFile = File(...)
):
    # O serviço será injetado pela configuração da aplicação.
    # Validar usuário, formato, tamanho e autorização.

    return {
        "mensagem": "Solicitação de upload recebida",
        "arquivo": arquivo.filename
    }


@router.get("/")
async def listar_documentos():
    # documento_service.listar_documentos()
    pass


@router.get("/{id_documento}")
async def obter_documento(id_documento: str):
    # documento_service.buscar_por_id()
    pass
