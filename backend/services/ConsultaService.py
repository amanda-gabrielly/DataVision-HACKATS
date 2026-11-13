
class ConsultaService:

    def __init__(
        self,
        consulta_repository,
        autorizacao_service,
        busca_semantica_service,
        ia_service,
        fonte_service,
        resultado_repository
    ):
        self.consulta_repository = consulta_repository
        self.autorizacao_service = autorizacao_service
        self.busca_semantica_service = busca_semantica_service
        self.ia_service = ia_service
        self.fonte_service = fonte_service
        self.resultado_repository = resultado_repository

    async def processar_pergunta(
        self,
        consulta,
        usuario
    ):

        consulta.validar_pergunta()

        self.consulta_repository.salvar(consulta)

        # Recuperar apenas documentos autorizados.
        trechos = await self.busca_semantica_service.buscar(
            consulta=consulta,
            usuario=usuario
        )

        resultado = await self.ia_service.gerar_resposta(
            pergunta=consulta.pergunta,
            trechos=trechos
        )

        fontes = await self.fonte_service.registrar_fontes(
            resultado=resultado,
            trechos=trechos
        )

        self.resultado_repository.salvar(resultado)

        return {
            "resultado": resultado,
            "fontes": fontes
        }
