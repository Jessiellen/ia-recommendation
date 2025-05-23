### O que o Projeto Faz

O projeto `ia-recommendation` é uma aplicação web que fornece **recomendações de produtos personalizadas** para usuários. Ele integra um sistema de backend robusto (FastAPI com PostgreSQL) com capacidades de Geração de Linguagem Natural (NLG) através de um Large Language Model (LLM) hospedado localmente via Ollama e orquestrado pelo framework CrewAI.

A ideia principal é que, a partir do perfil do usuário e de seus produtos cadastrados (se houver), um "Agente Especialista em Recomendação de Produtos" (definido no CrewAI) utilize o poder do LLM para gerar sugestões relevantes e com justificativas claras. Em caso de falha na interação com o LLM, o sistema possui um mecanismo de fallback que retorna recomendações genéricas, garantindo que o usuário sempre receba alguma sugestão.

### Desafios de Implementação e Como Foram Resolvidos

A implementação deste projeto apresentou alguns desafios notáveis, principalmente na integração do LLM local com as bibliotecas Python e na orquestração Docker:

1.  **Integração do LLM Local (Ollama/LangChain/CrewAI):**
    * **Desafio:** O maior obstáculo foi fazer a LangChain (especificamente `ChatOllama`) e o CrewAI se comunicarem de forma estável com o servidor Ollama rodando em um contêiner Docker separado. Erros comuns incluíam `404 Not Found` (quando o nome do modelo não era reconhecido) e `LLM Provider NOT provided` (quando a biblioteca `litellm` não conseguia inferir que estava a falar com o Ollama).
    * **Resolução:** Após várias tentativas e depurações intensivas dos logs do Docker (`web` e `ollama`), identificamos que o nome do modelo precisava ser exato (`llama2:7b-chat-q2_K`) e que a `ChatOllama` se beneficiava da especificação explícita do `ollama_url`. Além disso, a definição da variável de ambiente `OLLAMA_BASE_URL` via `os.environ` no código Python (antes da inicialização do LLM) foi crucial para que a `litellm` (usada internamente pela LangChain) reconhecesse o provedor Ollama corretamente. Isso garantiu que a conexão fosse estabelecida e que as requisições chegassem ao modelo.

2.  **Orquestração Docker:**
    * **Desafio:** Garantir que todos os serviços (PostgreSQL, Ollama, FastAPI) iniciassem na ordem correta e pudessem se comunicar entre si dentro da rede Docker. Problemas de `verbose` mal configurado no CrewAI também geraram `ValidationErrors`.
    * **Resolução:** A utilização de `docker compose` com a tag `--build` para reconstruir a imagem `web` após cada alteração de código Python foi essencial. O uso de `depends_on` no `docker-compose.yml` para os serviços assegurou a ordem de inicialização. A depuração dos logs do serviço `web` revelou o erro de `verbose=2` que foi corrigido para `verbose=True`, permitindo que o CrewAI fosse inicializado corretamente.

3.  **Parsers de Saída do LLM:**
    * **Desafio:** As respostas de LLMs podem ser inconsistentes no formato, o que dificultava a extração programática das recomendações.
    * **Resolução:** Implementamos um `PydanticOutputParser` da LangChain com um esquema Pydantic bem definido. Isso forçou o LLM a seguir um formato JSON específico. Combinado com um prompt detalhado que instrui o LLM sobre o formato de saída esperado, isso aumentou a robustez da extração das recomendações. A depuração constante dos "logs brutos" do LLM (o que ele realmente respondia) foi fundamental para ajustar o prompt e o parser.

Em resumo, o projeto superou desafios de integração complexos entre diferentes frameworks de IA e ambientes em contêineres, resultando em uma aplicação funcional capaz de gerar recomendações personalizadas, com resiliência a falhas do LLM através de um mecanismo de fallback.