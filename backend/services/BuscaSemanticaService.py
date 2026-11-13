
class BuscaSemanticaService:

    def __init__(
        self,
        trecho_repository,
        autorizacao_service,
        embeddings_service
    ):
        self.trecho_repository = trecho_repository
        self.autorizacao_service = autorizacao_service
        self.embeddings_service = embeddings_service

    async def buscar(self, consulta, usuario):

        vetor = await self.embeddings_service.gerar_embedding(
            consulta.pergunta
        )

        # A busca deve filtrar documentos autorizados
        # antes de retornar os trechos ao serviço de IA.

        trechos = await self.trecho_repository.buscar_semelhantes(
            vetor=vetor,
            id_usuario=usuario.id_usuario,
            id_perfil=usuario.id_perfil
        )

        return trechos
