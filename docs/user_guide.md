# Guia de Usuário e Utilização

Este guia detalha como usar a API e como instalar e executar o projeto `ia-recommendation` localmente.

## Uso da API

A API de recomendação de produtos é acessível via HTTP.

### Autenticação

Todos os endpoints que exigem autenticação requerem um **token JWT**.

1.  **Obter Token:**
    * Acesse `http://localhost:8000/docs`.
    * Expanda o endpoint `POST /api/v1/token`.
    * Clique em "Try it out".
    * Em "Request body", insira o `username` e `password` (ex: `alice`/`wonderland` ou crie um novo usuário via `POST /api/v1/users/`).
    * Clique em "Execute".
    * Copie o `access_token` da resposta.

2.  **Autorizar Requisições:**
    * Clique no botão "Authorize" (canto superior direito do Swagger UI).
    * No campo "Value", insira `Bearer SEU_TOKEN_AQUI` (substitua `SEU_TOKEN_AQUI` pelo token copiado, sem aspas).
    * Clique em "Authorize" e depois em "Close".

### Endpoints Principais

* **`GET /api/v1/recommendations/`:**
    * **Descrição:** Retorna uma lista de recomendações de produtos personalizadas para o usuário autenticado.
    * **Autenticação:** Sim (token JWT necessário).
    * **Parâmetros:** Nenhum.
    * **Resposta (Exemplo):**
        ```json
        [
          {
            "product_id": 123,
            "product_name": "Caneca de Café Sustentável",
            "reason": "Excelente para quem se preocupa com o meio ambiente e adora café."
          },
          {
            "product_id": 456,
            "product_name": "Kit de Jardinagem para Apartamento",
            "reason": "Perfeito para entusiastas que buscam adicionar verde ao seu espaço."
          }
        ]
        ```
    * **Fallback:** Em caso de falha na geração de recomendações pelo LLM, uma lista padrão de recomendações de fallback será retornada.

* **`POST /api/v1/users/`:**
    * **Descrição:** Cria um novo usuário no sistema.
    * **Autenticação:** Não.
    * **Corpo da Requisição (Exemplo):**
        ```json
        {
          "username": "novo_usuario",
          "email": "novo.usuario@example.com",
          "password": "uma_senha_segura"
        }
        ```

* **`GET /api/v1/users/me/`:**
    * **Descrição:** Retorna os detalhes do usuário autenticado.
    * **Autenticação:** Sim.

---

## Guia de Instalação e Utilização Local

Este guia assume que você tem **Docker** e **Docker Compose** instalados em sua máquina.

### 1. Clonar o Repositório

```bash
git clone [https://github.com/seu-usuario/ia-recommendation.git](https://github.com/seu-usuario/ia-recommendation.git)
cd ia-recommendation

### 2 Configurar Variáveis de Ambiente (Opcional, mas recomendado)


Crie um arquivo .env na raiz do projeto (o mesmo diretório do docker-compose.yml) e adicione as seguintes variáveis:

# Exemplo de .env
DATABASE_URL=postgresql://user:password@db:5432/mydatabase
SECRET_KEY=sua_super_chave_secreta_aqui_para_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OLLAMA_BASE_URL=http://ollama:11434
Observação: A SECRET_KEY deve ser uma string longa e aleatória para segurança da aplicação.

3. Iniciar os Serviços com Docker Compose

Este comando construirá as imagens Docker (se necessário) e iniciará todos os serviços definidos no docker-compose.yml em segundo plano.



docker compose up --build -d


4. Puxar o Modelo LLM para o Ollama

O Ollama precisa ter o modelo de linguagem grande baixado. Para este projeto, usamos llama2:7b-chat-q2_K.

docker exec -it ia-recommendation-ollama-1 ollama pull llama2:7b-chat-q2_K
Pode levar alguns minutos, dependendo da sua conexão com a internet, pois o modelo tem alguns GBs.

5. Executar Migrações do Banco de Dados

Para criar as tabelas do banco de dados (usuários, produtos, etc.):


docker exec -it ia-recommendation-web-1 alembic upgrade head

6. Acessar a Aplicação
A aplicação estará disponível em http://localhost:8000.

Documentação Interativa da API (Swagger UI): http://localhost:8000/docs
Documentação ReDoc: http://localhost:8000/redoc

7. Parar os Serviços
Quando quiser parar a aplicação:

docker compose down

Isso para e remove os contêineres, redes e volumes (exceto volumes nomeados que você pode ter definido).

### 3. O Relatório Breve

O sistema é projetado para ser usado como um backend para uma aplicação de e-commerce, plataforma de conteúdo, ou qualquer sistema que precise de recomendações de produtos/serviços personalizadas, impulsionadas por IA.

Fluxo de Uso Típico:

Usuário/Cliente: Interage com a API FastAPI (ex: via um frontend, mobile app, ou outra API).
Autenticação: O usuário pode se registrar e fazer login para obter um token JWT. Este token é usado para autenticar requisições a endpoints protegidos.
Requisição de Recomendação: O cliente envia uma requisição ao endpoint de recomendação (ex: /recommendations/generate) com o ID do usuário e/ou uma consulta (query).
Processamento pelo Backend:
A API valida a requisição.
Consulta o PostgreSQL para dados relevantes (perfil do usuário, histórico, produtos existentes).
Invoca os agentes CrewAI, passando o contexto do usuário e a consulta.
Geração de Recomendação (CrewAI + Ollama):
Os agentes CrewAI recebem o contexto e a consulta.
Interagem com o modelo LLM hospedado no Ollama para "raciocinar" e gerar recomendações de produtos baseadas no contexto fornecido.
Retornam uma lista de IDs de produtos e razões para as recomendações.
Resposta da API : A API FastAPI formata as recomendações e as retorna ao cliente.
3. Guia do Usuário para Instalação e Utilização
Este guia é para colocar o projeto para rodar rapidamente.

3.1. Pré-requisitos

Docker e Docker Compose : Instalandodocker.com.
Python 3.9+: Baixe de python.org.
Poesia : Instale com pip install poetry.

3.2. Instalação (Uma Só Vez)

Clone o Projeto:
Abra seu terminal e navegue até o diretório onde deseja armazenar o projeto.

git clone <URL_DO_SEU_REPOSITORIO> # Substitua pela URL real do seu repositório
cd ia-recommendation # Entre na pasta do projeto

Instale as Dependências Python:

poetry install --with dev
Isso cria um ambiente virtual e instala todas as bibliotecas necessárias.

Crie os Arquivos de Configuração (.env):
Quepasta principal do projeto(ia-recommendation),crie dois arquivos:

.env (para o uso normal/desenvolvimento):

Fragmento do código

DATABASE_URL="postgresql://user:password@db:5432/ia_recommendation"
SECRET_KEY="SUA_CHAVE_SECRETA_MUITO_FORTE_E_UNICA_PARA_PRODUCAO_OU_DEV"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
OLLAMA_BASE_URL="http://ollama:11434"
DB_ECHO_LOGS=False
TESTING=False
Altere SECRET_KEY para uma chave forte e exclusiva!

.env.test (para os testes automáticos):

Fragmento do código

DATABASE_URL="sqlite:///./test.db"
SECRET_KEY="SUA_CHAVE_SECRETA_DE_TESTE_APENAS_PARA_TESTES"
OLLAMA_BASE_URL="http://ollama:11434"
TESTING=True

3.3. Utilização
Inicie o Banco de Dados e o Servidor de IA (Ollama):
Crie um arquivo docker-compose.ymlquepasta principal do projeto:

YAML

version: '3.8'
services:
  db:
    image: postgres:15-alpine
    container_name: ia_recommendation_db
    environment:
      POSTGRES_DB: ia_recommendation
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports: ["5432:5432"]
    volumes: ["db_data:/var/lib/postgresql/data"]
    restart: unless-stopped
  ollama:
    image: ollama/ollama:latest
    container_name: ollama_llm
    ports: ["11434:11434"]
    volumes: ["ollama_data:/root/.ollama"]
    restart: unless-stopped
volumes:
  db_data:
  ollama_data:
Nenhum terminal, na pasta principal do projeto:

Bash

docker compose up -d # Inicia os serviços em segundo plano
Baixe um modelo para o Ollama (apenas na primeira vez):

Bash

docker exec -it ollama_llm ollama run llama3 # Baixa o modelo Llama3
# Digite /bye e Enter para sair do terminal do Ollama.
Crie as Tabelas do Banco de Dados:

Bash

poetry run python -c "from app.database import create_tables; create_tables()"
Isso configura o banco de dados para a sua aplicação.

Inicie a API do Projeto:

Bash

poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Sua API estará acessível emhttp://localhost:8000.

Acesse a Documentação da API (Swagger UI):
Abra seu navegador e vá para http://localhost:8000/docs. Aqui você pode explorar e testar os endpoints da API.

Rodar os Testes (Opcional, mas Recomendado):
Para garantir que tudo está funcionando:

Bash

poetry run pytest -s
Isso executa todos os testes do projeto.

Parar os Serviços (Quando terminar):
Para desligar o banco de dados e o Ollama:


docker compose down # Para os serviços
# Se quiser apagar os dados do banco de dados também:
# docker compose down --volumes

4. Documentação de API Gerada Automaticamente (FastAPI)
O FastAPI gera automaticamente uma documentação interativa da sua API no formato OpenAPI (anteriormente Swagger).

URL da Documentação (Swagger UI): http://localhost:8000/docs
URL da Documentação (ReDoc): http://localhost:8000/redoc
Esta documentação permite:

Visualizar todos os endpoints disponíveis, seus métodos HTTP, caminhos e descrições.
Ver os esquemas de requisição (request body) e resposta (response schemas) para cada endpoint, incluindo tipos de dados e validações.
Interagir com a API diretamente no navegador:enviar requisições de teste e ver as respostas.
Autenticar-se (se houver mecanismos de segurança configurados, como JWT) para testar endpoints protegidos.

### Relatório Breve do Projeto

1. O que o Projeto Faz
Este projeto implementa um Sistema de Recomendação de IA. Ele fornece uma API RESTful para gerenciar usuários e, mais importante, gerar recomendações personalizadas. A inteligência de recomendação é impulsionada por agentes de IA (CrewAI) que utilizam um Large Language Model (LLM) hospedado localmente (Ollama) para interpretar requisições e fornecer sugestões contextuais.

Em resumo, ele permite:

Gerenciar usuários:Registro, login e perfil.
Autenticação segura:Usando JWT para proteger endpoints.
Recomendações Inteligentes: Gera recomendações de produtos/itens com base em consultas do usuário e/ou perfil,usando agentes de IA para um raciocínio mais complexo.
Infraestrutura Local: Permite rodar o banco de dados e o LLM completamente na sua máquina, ideal para desenvolvimento e testes.

2. Desafios de Implementação e Como Foram Resolvidos

A implementação deste projeto apresentou vários desafios, típicos de sistemas que integram múltiplas tecnologias e componentes de IA:

Configuração de Ambiente e Variáveis de Ambiente (.env):

Desafio: Garantir que as variáveis de ambiente fossem carregadas corretamente pelo aplicativo FastAPI e,crucialmente, pelo Pytest, especialmente porque a classe Settings(pydantic-settings) era inicializada muito cedo. Problemas com ValidationErrordeDATABASE_URLeSECRET_KEY eram persistentes.
Resolução:
Para o ambiente de desenvolvimento: O load_dotenv()nãomain.py e a ordem de importação foram cuidadosamente gerenciados.
Para os testes (Pytest): A solução mais robusta foi usar o hook pytest_configurenãoconftest.py. Este hook é executado muito cedo no ciclo de vida do Pytest, garantindo que load_dotenv() seja chamado e as variáveis de ambiente estejam disponíveis antes que a classe Settings seja inicializada por qualquer import de módulo da aplicação. A injeção direta via comando DATABASE_URL=... poetry run pytest também foi uma ferramenta de depuração chave para confirmar o problema de carregamento.
Compatibilidade do SQLite3 com chromadb (CrewAI):

Desafio: O chromadb,uma dependência transitiva do CrewAI (usada para cache de incorporação), exigia uma versão mais recente do SQLite3 do que a fornecida por padrão no ambiente do Codespaces/Python. Isso resultava em RuntimeError: Your system has an unsupported version of sqlite3.
Resolução: Implementou-se um "monkey patch" no conftest.pyusando a bibliotecapysqlite3-binary. Ao importar pysqlite3 e sobrescrever sys.modules["sqlite3"], forçamos o Python a usar a versão mais recente do SQLite3 empacotada com pysqlite3-binary, resolvendo o conflito. A ordem do monkey patchnãoconftest.py (antes dos imports da aplicação) foi crucial.
Permissão de Escrita para Logging (PermissionError):

Desafio: O sistema de logging padrão tentava criar um arquivo app.log na raiz do projeto, o que resultava em PermissionError em ambientes restritivos como o Codespaces.
Resolução: Modificou-se a função setup_logging() em app/core/app_logging.py. Adicionou-se uma condição para que o RotatingFileHandler (que escreve em arquivo) só seja inicializado se a variável de ambiente TESTINGparaFalse. Para testes, o logging é direcionado apenas para o console. Além disso, a pasta de logs foi definida para um local com permissão de escrita (ex: um subdiretório logs na raiz do projeto ou /tmp/app_logs).
Problemas de Importação e Definição de Fixtures (Linter/Ruff):

Desafio: Erros como Undefined name (para get_test_db, Generator) e Redefinition of unused(parasetup_test_database) surgiram durante a refatoração do conftest.py e a adição de type hints.
Resolução: Foram feitas correções diretas nas declarações de import (garantindo que todas as entidades usadas estivessem importadas de seus respectivos módulos, como GeneratoreAnydetyping).UMRedefinition foi resolvida identificando e removendo uma definição duplicada de um fixture (setup_test_database foi acidentalmente duplicado e seu propósito misturado com db_session), e aplicando as type hints corretamente para as funções geradoras.` na raiz do seu projeto ou dentro da pasta `docs` mesmo, se preferir. Um bom lugar seria na raiz para que seja facilmente visível.

