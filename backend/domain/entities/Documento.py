
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Documento:
    id_documento: UUID
    codigo: str
    titulo: str
    tipo: str
    categoria: str
    classificacao: str
    criado_por: UUID
    criado_em: datetime

    def alterar_classificacao(self, classificacao: str):
        self.classificacao = classificacao

    def alterar_categoria(self, categoria: str):
        self.categoria = categoria
