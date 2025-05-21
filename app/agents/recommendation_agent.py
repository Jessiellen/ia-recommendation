from crewai import Agent, Task, Crew
import os
from dotenv import load_dotenv

load_dotenv()

class RecommendationAgent:
    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL")

    def generate_recommendations(self, user):
        recommendation_agent = Agent(
            role='Product Recommendation Specialist',
            goal='Provide personalized product recommendations',
            backstory='You are an AI agent specialized in analyzing user behavior and recommending products.',
            allow_delegation=False,
            llm_model='llama2', 
            llm_base_url=self.ollama_base_url
        )

        recommendation_task = Task(
            description=f'Analyze the user {user.username} and their product history. Generate 3 personalized product recommendations.',
            agent=recommendation_agent
        )

        crew = Crew(
            agents=[recommendation_agent],
            tasks=[recommendation_task]
        )

        result = crew.kickoff()

        
        recommendations = [
            {"product_id": 1, "product_name": "Product A", "reason": "Based on your history"},
            {"product_id": 2, "product_name": "Product B", "reason": "Popular among similar users"},
            {"product_id": 3, "product_name": "Product C", "reason": "New arrival in your favorite category"}
        ]

        return recommendations