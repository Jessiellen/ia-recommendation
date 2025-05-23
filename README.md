🚀 Sistema de Recomendação de Produtos com IA
Este projeto é um sistema de recomendação de produtos inteligente, construído com FastAPI, CrewAI e um Large Language Model (LLM) rodando localmente via Ollama. Ele fornece recomendações personalizadas para usuários, utilizando o poder da inteligência artificial para entender suas necessidades e sugerir produtos relevantes.

✨ Funcionalidades
Recomendações Personalizadas: Sugestões com base nas preferências do usuário usando um LLM.

Agentes de IA: Uso do CrewAI para orquestração inteligente com agentes autônomos.

LLM Local: Modelo llama2:7b-chat-q2_K executado via Ollama.

API RESTful: Backend robusto com FastAPI.

Autenticação JWT: Segurança via tokens.

Banco de Dados PostgreSQL

Docker Compose: Setup simples e portátil.

Documentação Swagger/OpenAPI

Fallback Inteligente: Recomendações padrão em caso de erro no LLM.

🏗️ Arquitetura

Usuário/Cliente
       ↓
 FastAPI (Web) ───→ CrewAI Agent ───→ Ollama (LLM)
       ↓
  PostgreSQL
FastAPI: Interface REST, autenticação e integração com agentes.

CrewAI: Orquestração de agentes de recomendação via LangChain.

Ollama: Execução local do modelo LLM.

PostgreSQL: Armazenamento persistente.

Docker Compose: Infraestrutura containerizada.

⚙️ Instalação e Execução
Pré-requisitos: Docker + Docker Compose

1. Clonar o Projeto

git clone https://github.com/seu-usuario/ia-recommendation.git
cd ia-recommendation

2. Configurar o .env
Crie um arquivo .env na raiz:

env

DATABASE_URL=postgresql://user:password@db:5432/mydatabase
SECRET_KEY=sua_super_chave_secreta
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OLLAMA_BASE_URL=http://ollama:11434

3. Subir os Contêineres


docker compose up --build -d

4. Baixar o Modelo LLM

docker exec -it ia-recommendation-ollama-1 ollama pull llama2:7b-chat-q2_K

5. Migrar o Banco de Dados

docker exec -it ia-recommendation-web-1 alembic upgrade head

6. Acessar a Aplicação
Swagger: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc

🔐 Autenticação

Criar usuário: POST /api/v1/users/

Obter token: POST /api/v1/token

Usar token JWT: clique em "Authorize" no Swagger e adicione Bearer SEU_TOKEN_AQUI.

🔑 Endpoints Principais

POST /api/v1/users/ – Cria usuário.

POST /api/v1/token – Gera token de acesso.

GET /api/v1/users/me/ – Retorna dados do usuário.

GET /api/v1/recommendations/ – Lista de recomendações personalizadas.

🛠️ Desafios Técnicos

1. Integração com Ollama
Problema: Erros como "modelo não encontrado" e "LLM provider not provided".

Solução: Garantir nome exato do modelo, definir OLLAMA_BASE_URL e configurar ChatOllama corretamente no código.

2. Orquestração com Docker
Problema: Ordem de inicialização e dependências entre serviços.

Solução: Uso de depends_on, rebuild frequente com --build, logs para debug.

3. Parsing de Respostas do LLM
Problema: Formatos de resposta inconsistentes.

Solução: PydanticOutputParser com esquema bem definido e prompts específicos para o formato JSON.

🤝 Contribuições

Pull requests e issues são bem-vindos!

📄 Licença

Distribuído sob a licença MIT. Veja LICENSE para mais detalhes.

