from typing import List, Optional
import re
import asyncio
import logging
import os

from crewai import Agent, Task, Crew
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage 

from app.schemas import Recommendation
from app.models import User as UserModel
from app.core.config import settings

logger = logging.getLogger(__name__)

class RecommendationAgent:
    def __init__(self):
        """Inicializa o agente de recomendação com configurações do Ollama."""
        self.ollama_base_url = settings.OLLAMA_BASE_URL
        self.model_name = "llama2:7b-chat-q2_K" 

        try:
            os.environ["OLLAMA_BASE_URL"] = self.ollama_base_url
            self.ollama_llm_instance = ChatOllama(
                base_url=self.ollama_base_url,
                model=self.model_name,
                temperature=0.7,
                ollama_url=self.ollama_base_url
            )
            test_message = "Hello, check Ollama connection."
            test_output = self.ollama_llm_instance.invoke([HumanMessage(content=test_message)])
            logger.info(f"Ollama connection test successful. Input: '{test_message}'. Output snippet: '{test_output.content[:50]}...'")
        except Exception as e:
            logger.error(f"Falha ao inicializar ou conectar ao Ollama LLM: {str(e)}. Verifique se o serviço 'ollama' está rodando e o modelo '{self.model_name}' foi puxado.", exc_info=True)
            raise 

    async def generate_recommendations(self, user_model: UserModel, user_products_info: str) -> List[Recommendation]:
        """
        Gera recomendações de produtos personalizadas para o usuário usando CrewAI e Ollama.

        Args:
            user_model: Objeto UserModel contendo informações do usuário (do DB).
            user_products_info: String formatada com o histórico de produtos do usuário.

        Returns:
            Lista de recomendações de produtos
        """
        try:
            recommendation_agent = Agent(
                role='Especialista em Recomendação de Produtos',
                goal='Fornecer recomendações de produtos personalizadas e relevantes baseadas no perfil e histórico do usuário',
                backstory=(
                    'Você é um especialista em análise de comportamento do usuário e histórico de compras/interações '
                    'para gerar recomendações de produtos altamente relevantes. Use as informações do usuário e '
                    'seu histórico de produtos para criar as melhores sugestões.'
                ),
                allow_delegation=False, 
                llm=self.ollama_llm_instance,
                verbose=True 
            )

            recommendation_task = Task(
                description=f'''Analise cuidadosamente o usuário {user_model.username} (ID: {user_model.id}, Email: {user_model.email}).
                O histórico de produtos do usuário é: {user_products_info}.
                
                **Seu objetivo é gerar EXATAMENTE 3 (três) recomendações de produtos únicas, personalizadas e variadas que o usuário provavelmente se interessaria, baseando-se no histórico fornecido.**

                **FORMATO DE SAÍDA OBRIGATÓRIO (MUITO IMPORTANTE):**
                Cada recomendação DEVE ser uma linha separada e formatada EXATAMENTE assim:
                `Product ID: <um número inteiro único>, Name: <o nome do produto>, Reason: <a razão detalhada para a recomendação>`

                **REGRAS RÍGIDAS DE FORMATAÇÃO:**
                1.  NÃO INCLUA NENHUM TEXTO INTRODUTÓRIO OU CONCLUSIVO. APENAS AS 3 LINHAS FORMATADAS.
                2.  Garanta que cada `Product ID` seja um número inteiro.
                3.  O `Name` e `Reason` podem conter qualquer texto, mas devem estar na mesma linha que "Product ID".

                **EXEMPLO DE SAÍDA PERFEITA (SIGA ESTE FORMATO EXATAMENTE):**
                Product ID: 101, Name: Tênis de Corrida Leve, Reason: Ideal para iniciantes, com bom amortecimento para corridas diárias.
                Product ID: 102, Name: Livro "A Arte de Persuadir", Reason: Útil para desenvolvimento profissional e habilidades de comunicação.
                Product ID: 103, Name: Cafeteira Expresso Compacta, Reason: Perfeita para amantes de café que buscam praticidade e qualidade.
                ''',
                agent=recommendation_agent,
                expected_output='''Lista de 3 recomendações formatadas exatamente como:
                Product ID: <id>, Name: <nome>, Reason: <razão>
                '''
            )

            crew = Crew(
                agents=[recommendation_agent],
                tasks=[recommendation_task],
                verbose=True 
            )

            
            result = await asyncio.to_thread(crew.kickoff)
            logger.info(f"CrewAI kickoff finalizado para o usuário {user_model.username}. Resultado bruto:\n{result}")

            return self._parse_crew_result(result)

        except Exception as e:
            logger.error(f"Erro ao gerar recomendações para {user_model.username}: {str(e)}", exc_info=True)
            return self._get_fallback_recommendations()

    def _parse_crew_result(self, result: str) -> List[Recommendation]:
        """
        Analisa o resultado bruto do CrewAI e extrai as recomendações.
        Este parser é mais robusto para lidar com pequenas variações do LLM.
        """
        recommendations = []

        pattern = re.compile(
            r"Product ID:\s*(\d+)\s*,\s*Name:\s*(.+?)\s*,\s*Reason:\s*(.+?)\s*(?=\nProduct ID:|\Z|$)",
            re.DOTALL | re.IGNORECASE
        )

        try:
            matches = pattern.finditer(result)
            for match in matches:
                try:
                    product_id = int(match.group(1).strip()) 
                    product_name = match.group(2).strip()
                    reason = match.group(3).strip()
                    recommendations.append(
                        Recommendation(
                            product_id=product_id,
                            product_name=product_name,
                            reason=reason
                        )
                    )
                except (ValueError, IndexError) as e:
                    logger.warning(f"Falha ao analisar uma recomendação individual do LLM. Trecho: '{match.group(0).strip()}'. Erro: {e}")

        except Exception as e:
            logger.error(f"Erro inesperado ao aplicar regex no resultado do CrewAI: {e}", exc_info=True)

        # Garante que sempre retornamos 3 recomendações, adicionando fallbacks se necessário
        if len(recommendations) < 3:
            logger.warning(f"Apenas {len(recommendations)} recomendações válidas foram extraídas do LLM. Adicionando fallbacks.")
            fallbacks_needed = 3 - len(recommendations)
            recommendations.extend(self._get_fallback_recommendations()[:fallbacks_needed])

        # Garante que o resultado final tenha no máximo 3 recomendações
        return recommendations[:3]

    def _get_fallback_recommendations(self) -> List[Recommendation]:
        """Retorna recomendações genéricas de fallback."""
        logger.info("Retornando recomendações de fallback.")
        return [
            Recommendation(
                product_id=901,
                product_name="Livro Bestseller de Ficção",
                reason="Um dos livros mais vendidos no momento, elogiado pela crítica e leitores."
            ),
            Recommendation(
                product_id=902,
                product_name="Fone de Ouvido Sem Fio (Cancelamento de Ruído)",
                reason="Ideal para trabalho remoto ou viagens, proporcionando imersão total."
            ),
            Recommendation(
                product_id=903,
                product_name="Planta Decorativa para Casa (Fácil Cuidado)",
                reason="Adiciona um toque de natureza ao ambiente e melhora a qualidade do ar, requerendo pouca manutenção."
            )
        ]