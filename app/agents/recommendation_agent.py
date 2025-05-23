from typing import List
import re
import asyncio
from crewai import Agent, Task, Crew
from app.schemas import User, Recommendation 
from app.models import User as UserModel 
from app.core.config import settings
import logging
from langchain_community.llms import Ollama

logger = logging.getLogger(__name__)

class RecommendationAgent:
    def __init__(self):
        """Inicializa o agente de recomendação com configurações do Ollama."""
        self.ollama_base_url = settings.OLLAMA_BASE_URL

        try:
            self.ollama_llm_instance = Ollama(
                base_url=self.ollama_base_url,
                model="llama2",  
                temperature=0.7  
            )
            test_output = self.ollama_llm_instance.invoke("Hello, check connection.")
            logger.info(f"Ollama connection test successful. Output snippet: {test_output[:50]}...")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama LLM or connect: {str(e)}")
            raise

    async def generate_recommendations(self, user_model: UserModel, user_products_info: str) -> List[Recommendation]:
        """
        Gera recomendações de produtos personalizadas para o usuário.

        Args:
            user_model: Objeto UserModel contendo informações do usuário (do DB, com produtos carregados).
            user_products_info: String formatada com o histórico de produtos do usuário.

        Returns:
            Lista de recomendações de produtos
        """
        try:
            recommendation_agent = Agent(
                role='Especialista em Recomendação de Produtos',
                goal='Fornecer recomendações de produtos personalizadas e relevantes',
                backstory='Você é um especialista em análise de comportamento do usuário e histórico de compras/interações para gerar recomendações de produtos altamente relevantes. Use as informações do usuário e seu histórico de produtos para criar as melhores sugestões.',
                allow_delegation=False,
                llm=self.ollama_llm_instance,
                verbose=True  
            )

            recommendation_task = Task(
                description=f'''Analise o usuário {user_model.username} (ID: {user_model.id}, Email: {user_model.email}).
                Histórico de produtos do usuário: {user_products_info}.
                Com base nessas informações, gere 3 recomendações de produtos personalizadas e variadas que o usuário provavelmente se interessaria.
                Formate cada recomendação exatamente como:
                Product ID: <id>, Name: <nome do produto>, Reason: <razão detalhada para a recomendação>''',
                agent=recommendation_agent,
                expected_output='''Lista de 3 recomendações formatadas como:
                Product ID: 123, Name: Nome do Produto Exemplo, Reason: Razão detalhada pela qual o produto foi recomendado.
                Product ID: 456, Name: Outro Produto Sugerido, Reason: Explicar o porquê da segunda recomendação.
                Product ID: 789, Name: Terceira Opção, Reason: Justificar a terceira recomendação.'''
            )

            crew = Crew(
                agents=[recommendation_agent],
                tasks=[recommendation_task],
                verbose=2  
            )

            result = await asyncio.to_thread(crew.kickoff)
            logger.info(f"Recomendações geradas para o usuário {user_model.username}")

            return self._parse_crew_result(result)

        except Exception as e:
            logger.error(f"Erro ao gerar recomendações para {user_model.username}: {str(e)}", exc_info=True)
            return self._get_fallback_recommendations()

    def _parse_crew_result(self, result: str) -> List[Recommendation]:
        """
        Analisa o resultado bruto do CrewAI e extrai as recomendações.

        Args:
            result: String contendo o resultado bruto do CrewAI

        Returns:
            Lista de objetos Recommendation parseados
        """
        recommendations = []
        pattern = r"Product ID:\s*(\d+),\s*Name:\s*(.+?),\s*Reason:\s*(.+)"

        try:
            matches = re.finditer(pattern, result)
            for match in matches:
                try:
                    recommendations.append(
                        Recommendation(
                            product_id=int(match.group(1)),
                            product_name=match.group(2).strip(),
                            reason=match.group(3).strip()
                        )
                    )
                except (ValueError, IndexError) as e:
                    logger.warning(f"Falha ao analisar recomendação: '{match.group(0)}'. Erro: {e}")

        except Exception as e:
            logger.error(f"Erro inesperado ao analisar resultados do CrewAI: {e}", exc_info=True)

        #  3 recomendações, adicionando fallbacks 
        if len(recommendations) < 3:
            logger.warning(f"Apenas {len(recommendations)} recomendações válidas encontradas. Adicionando fallbacks.")
            fallbacks_needed = 3 - len(recommendations)
            recommendations.extend(self._get_fallback_recommendations()[:fallbacks_needed])

        return recommendations[:3]

    def _get_fallback_recommendations(self) -> List[Recommendation]:
        """Retorna recomendações genéricas de fallback."""
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