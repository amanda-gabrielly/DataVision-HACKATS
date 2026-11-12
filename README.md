# DataVision BBTS

**Transformando documentos corporativos em decisões mais claras.**

O DataVision BBTS é um MVP para organizar documentos corporativos e encontrar evidências importantes com rapidez. O sistema permite cadastrar PDFs, separá-los por área, tema e tipo, e consultar o conteúdo com referências ao arquivo e à página.

## O que funciona nesta etapa

- Envio de um ou vários PDFs pela aplicação.
- Extração de texto com número da página e nome do arquivo de origem.
- Organização por área, tema e tipo de documento.
- Identificação de título e tentativa de identificar versão e data pelo nome ou pelos metadados do PDF.
- Verificação de duplicidade pelo conteúdo exato do arquivo.
- Acompanhamento do processamento em lote e retorno individual de sucesso ou erro.
- Aviso claro quando um PDF parece digitalizado e não tem texto selecionável. OCR ainda não está ativo.
- Busca de trechos relacionados com referência ao documento, versão e página.
- Criação/atualização do esquema do PostgreSQL automaticamente quando a API inicia.

As consultas atuais usam busca textual local. A integração com um modelo de IA pode ser adicionada em outra etapa; nenhuma chave de API é necessária para executar o MVP atual.

## Tecnologias

- **Frontend:** React e Vite
- **Backend:** Python e FastAPI
- **Banco de dados:** PostgreSQL
- **Leitura de PDFs:** pypdf

## Pré-requisitos

- Node.js e npm
- Python
- PostgreSQL instalado e em execução
- Banco PostgreSQL chamado `datavision` para uso local

## Iniciar o backend no Windows

Abra um terminal PowerShell na pasta do projeto e execute:

```powershell
cd backend
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Informe a senha local do PostgreSQL sem deixá-la escrita no histórico do terminal e inicie a API:

```powershell
$secret = Read-Host "Senha local do PostgreSQL" -AsSecureString
$env:POSTGRES_PASSWORD = (New-Object System.Net.NetworkCredential("", $secret)).Password
python -m uvicorn main:app --reload
```

A API ficará em `http://127.0.0.1:8000`. A documentação interativa fica em `http://127.0.0.1:8000/docs`.

## Iniciar o frontend

Abra outro terminal PowerShell na pasta do projeto:

```powershell
cd frontend
npm install
npm run dev
```

Abra o endereço mostrado pelo Vite, normalmente `http://localhost:5173`.

## Banco compartilhado

Para apontar a API a um PostgreSQL compartilhado, configure a variável de ambiente `DATABASE_URL` no terminal do backend antes de iniciar a API. A conexão deve usar o driver PostgreSQL do projeto (`postgresql+psycopg://...`). Quando `DATABASE_URL` não estiver definida, a API usa o PostgreSQL local e a variável `POSTGRES_PASSWORD`.

Não coloque senhas, URLs completas com credenciais ou chaves de API no Git. Cada integrante deve configurar suas próprias variáveis de ambiente. O esquema é atualizado automaticamente ao iniciar a API; o SQL da migração também fica versionado em `backend/migrations/001_document_processing.sql`.

## Dados e segurança

Durante o hackathon, use apenas dados sintéticos ou anonimizados. Os PDFs não são guardados como arquivos pelo backend nesta etapa; são armazenados no banco o texto extraído, a página, o nome de origem e os metadados necessários para consulta.
