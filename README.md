# DataVision BBTS

**Transformando documentos corporativos em decisões mais claras.**

## Sobre o projeto

O DataVision BBTS é a proposta de um MVP de inteligência empresarial. A plataforma conecta documentos e dados corporativos a uma experiência simples de consulta, ajudando gestores a encontrar informações importantes e entender o que elas significam.

As respostas devem apontar para as fontes que as sustentam, incluindo documento, versão, página e trecho relevante.

## Problema

Manuais, contratos, normas e relatórios empresariais costumam ser extensos, complexos e distribuídos. Encontrar informações específicas pode consumir tempo e exigir apoio de especialistas.

## Solução proposta

Uma plataforma para organizar documentos por tema, permitir perguntas em linguagem natural e destacar informações por diferentes perspectivas, como riscos, prazos, obrigações e valores.

## Escopo do MVP

- Envio e organização de documentos PDF por tema.
- Extração e busca de trechos relevantes.
- Respostas acompanhadas de fontes e evidências.
- Síntese das informações por perspectiva de análise.
- Painel responsivo para consultar o acervo e os resultados.

## Tecnologias

- **Frontend:** React e Vite
- **Backend:** Python e FastAPI
- **Banco de dados:** PostgreSQL
- **Processamento de PDFs:** pypdf

A primeira versão está sendo preparada para funcionar sem chave externa de IA. A integração com um provedor de IA poderá ser adicionada depois.

## Como executar o frontend

Requisitos: Node.js e npm.

```powershell
cd frontend
npm install
npm run dev
```

O Vite exibirá o endereço local para abrir a aplicação no navegador.

## Estrutura do projeto

```text
DataVision-HACKATS/
├── frontend/       # Aplicação React
├── backend/        # API em Python
└── README.md
```

## Estado atual

O projeto está em desenvolvimento. A estrutura inicial do frontend foi criada e as dependências do backend foram instaladas. A configuração do PostgreSQL e a implementação das funcionalidades do MVP ainda estão em andamento.

## Dados e segurança

Durante o hackathon, use apenas dados sintéticos ou anonimizados. Não envie senhas, chaves de API ou credenciais para o repositório.
