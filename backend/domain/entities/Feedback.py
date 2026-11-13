
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Feedback:
    id_feedback: UUID
    id_resultado: UUID
    id_usuario: UUID
    avaliacao: int
    comentario: str | None
    criado_em: datetime

    def validar_avaliacao(self):
        if not 1 <= self.avaliacao <= 5:
            raise ValueError("Avaliação deve estar entre 1 e 5.")
