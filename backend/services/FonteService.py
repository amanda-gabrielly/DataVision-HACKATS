
class FonteService:

    def __init__(self, fonte_repository):
        self.fonte_repository = fonte_repository

    async def registrar_fontes(
        self,
        resultado,
        trechos,
        associacoes
    ):
        fontes = []

        # Cada fonte deverá receber:
        # id_resultado
        # id_consulta_documento
        # id_trecho
        # id_versao
        # citacao
        # pagina
        # confianca

        return await self.fonte_repository.salvar_varias(
            fontes
        )
