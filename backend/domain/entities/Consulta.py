
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Consulta:
    id_consulta: UUID
    id_usuario: UUID
    pergunta: str
    data_consulta: datetime

    def validar_pergunta(self):
        if not self.pergunta.strip():
            raise ValueError("A pergunta não pode estar vazia.")
