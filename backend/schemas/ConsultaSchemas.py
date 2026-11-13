
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ConsultaCreate(BaseModel):
    pergunta: str = Field(
        min_length=3,
        max_length=5000,
        description="Pergunta enviada pelo usuário à IA"
    )


class ConsultaResponse(BaseModel):
    id_consulta: UUID
    id_usuario: UUID
    pergunta: str
    data_consulta: datetime

    model_config = ConfigDict(from_attributes=True)
