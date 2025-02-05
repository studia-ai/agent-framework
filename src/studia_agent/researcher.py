from typing import List
from crewai import Crew
from .services.token_service import TokenService
from .agents import create_token_analysis_agents, create_token_tasks

class TokenAnalyzer:
    def __init__(self):
        self.token_service = TokenService()

    def analyze_token(self, token_address: str):
        # Create specialized agents
        token_researcher, market_analyst, risk_analyst = create_token_analysis_agents(self.token_service)
        
        # Create crew for token analysis
        crew = Crew(
            agents=[token_researcher, market_analyst, risk_analyst],
            tasks=create_token_tasks(token_address, token_researcher, market_analyst, risk_analyst),
            verbose=True
        )
        
        result = crew.kickoff()
        return result 