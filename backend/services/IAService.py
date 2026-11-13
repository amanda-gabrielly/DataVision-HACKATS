
class IAService:

    def __init__(self, provedor_ia):
        self.provedor_ia = provedor_ia

    async def gerar_resposta(self, pergunta, trechos):

        contexto = [
            {
                "conteudo": trecho.conteudo,
                "pagina": trecho.pagina,
                "id_trecho": str(trecho.id_trecho)
            }
            for trecho in trechos
        ]

        resposta = await self.provedor_ia.processar(
            pergunta=pergunta,
            contexto=contexto
        )

        return resposta
