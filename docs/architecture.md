# Arquitetura do Sistema

O projeto `ia-recommendation` é uma aplicação web de recomendação de produtos construída com **FastAPI** e **CrewAI**, orquestrada via **Docker Compose**. Ela se comunica com um modelo de linguagem grande (LLM) hospedado localmente via **Ollama** e persiste dados em um banco de dados **PostgreSQL**.

Aqui está um diagrama simplificado da arquitetura:

+-------------------+      +-----------------+      +-----------------+      +-----------------+
|   Usuário/Cliente | ---->|   FastAPI (Web) | ---->|   CrewAI Agent  | ---->|     Ollama      |
| (Navegador/Swagger)|      | (Python/Uvicorn)|      | (LangChain/LLM) |      | (LLM Llama2)    |
+-------------------+      +-----------------+      +-----------------+      +-----------------+
^                            |
|                            | (Requisições HTTP/API)
|                            |
+----------------------------+
|
| (Conexão DB)
|
+----------------+
|   PostgreSQL   |
| (Banco de Dados)|
+----------------+

* **FastAPI (Serviço `web`):**
    * Serve como a interface RESTful para a aplicação.
    * Gera automaticamente a documentação da API (Swagger UI/OpenAPI) em `/docs`.
    * Gerencia a autenticação de usuários (JWT).
    * Orquestra a lógica de negócio, incluindo a chamada para o agente de recomendação.
    * Conecta-se ao PostgreSQL para buscar dados de usuários e produtos.

* **CrewAI Agent (Integração no Serviço `web`):**
    * Um framework para orquestrar agentes autônomos baseados em LLMs.
    * Define um `RecommendationAgent` (agente) e uma `Task` (tarefa) para gerar recomendações.
    * Utiliza `LangChain` para a integração com o LLM.

* **Ollama (Serviço `ollama`):**
    * Um servidor local para rodar modelos de linguagem grandes (LLMs).
    * Hospeda o modelo `llama2:7b-chat-q2_K` (ou outro modelo configurado).
    * Recebe requisições do serviço `web` (via LangChain/CrewAI) e retorna as previsões do LLM.

* **PostgreSQL (Serviço `db`):**
    * Banco de dados relacional para persistir informações de usuários e produtos.
    * A aplicação FastAPI interage com ele usando **SQLAlchemy** e **Alembic** (para migrações).

* **Docker Compose:**
    * Orquestra todos os serviços (web, ollama, db) em um ambiente isolado e reproduzível, facilitando a instalação e execução local.