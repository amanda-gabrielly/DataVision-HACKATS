
from app.domain.entities.trecho_documento import TrechoDocumento


class ProcessamentoDocumentoService:

    def __init__(self, extrator, storage, trecho_repository):
        self.extrator = extrator
        self.storage = storage
        self.trecho_repository = trecho_repository

    async def processar_documento(
        self,
        arquivo_path: str,
        id_versao
    ):

        arquivo = await self.storage.obter_arquivo(arquivo_path)

        texto = await self.extrator.extrair_texto(arquivo)

        trechos = self.extrator.dividir_em_trechos(texto)

        entidades = [
            TrechoDocumento(
                id_trecho=trecho["id"],
                id_versao=id_versao,
                conteudo=trecho["conteudo"],
                pagina=trecho["pagina"],
                ordem=indice
            )
            for indice, trecho in enumerate(trechos)
        ]

        return await self.trecho_repository.salvar_varios(
            entidades
        )
