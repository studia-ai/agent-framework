import os
from typing import List
from crewai import Agent, Task
from tavily import TavilyClient
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from .services.token_service import TokenService

# Initialize tools properly
def web_search(query: str) -> str:
    """Search the web for information about a topic."""
    try:
        tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        search_result = tavily.search(query=query)
        return str(search_result)
    except Exception as e:
        return f"Error searching: {str(e)}"

# Create tools
search_tool = Tool(
    name="WebSearch",
    func=web_search,
    description="Search the web for information. Input should be a simple search query string."
)

class TwitterTools:
    def __init__(self, twitter_client=None):
        self.twitter_client = twitter_client

    def post_tweet(self, content: str) -> str:
        if self.twitter_client is None:
            return f"[PREVIEW - No Twitter credentials] Tweet content: {content}"
        # Instead, just return what would be tweeted
        return f"[PREVIEW] Tweet content: {content}"

def create_twitter_agents(twitter_client=None, tavily_client=None):
    """Create the Twitter agents with both Twitter and Tavily clients."""
    twitter_tools = TwitterTools(twitter_client)
    twitter_tool = Tool(
        name="PostTweet",
        func=twitter_tools.post_tweet,
        description="Post a tweet to Twitter. Input should be the tweet content as a string."
    )

    # Update web_search to use the passed tavily_client
    def web_search(query: str) -> str:
        """Search the web for information about a topic."""
        try:
            if tavily_client:
                search_result = tavily_client.search(query=query)
                return str(search_result)
            else:
                return "Error: Tavily client not initialized"
        except Exception as e:
            return f"Error searching: {str(e)}"

    search_tool = Tool(
        name="WebSearch",
        func=web_search,
        description="Search the web for information. Input should be a simple search query string."
    )

    content_researcher = Agent(
        role='Social Media Research Intern',
        goal='Find relevant and accurate information about trending topics',
        backstory="""You're a research-focused intern who specializes in finding accurate 
        and relevant information. You focus on substance over style, ensuring all information 
        is factual and valuable. You always verify information through web searches.""",
        allow_delegation=False,
        tools=[search_tool],
        llm=ChatOpenAI(temperature=0.7, model="gpt-4"),
        verbose=True
    )

    content_writer = Agent(
        role='Professional Content Writer',
        goal='Write clear, concise tweets that fit Twitter\'s character limit',
        backstory="""You're a professional writer who specializes in extremely concise communication. 
        You must create tweets that are ALWAYS under 280 characters total (including ' prefix). 
        Never use quotes around the tweet. Never add multiple  prefixes. You avoid hashtags 
        completely and use emojis very sparingly (maximum one per tweet). You excel at summarizing 
        complex information in brief, impactful messages, focusing on the most essential points only.
        You verify facts before including them in tweets.""",
        allow_delegation=False,
        tools=[search_tool],
        llm=ChatOpenAI(temperature=0.7, model="gpt-4")
    )

    tweet_publisher = Agent(
        role='Content Quality Manager',
        goal='Ensure tweets are professional, appropriate, and within length limits',
        backstory="""You're the final checkpoint for content quality. You ensure tweets are 
        professional, accurate, and appropriate. You strictly enforce the 280 character limit 
        (including ' prefix). Never use quotes around tweets. Never allow multiple 
        prefixes. If a tweet is too long or has formatting issues, you rewrite it to 
        be correct while maintaining the key message. You remove any hashtags and ensure 
        minimal emoji usage. You fact-check claims before publishing.""",
        allow_delegation=False,
        tools=[twitter_tool, search_tool],
        llm=ChatOpenAI(temperature=0.7, model="gpt-4")
    )

    return content_researcher, content_writer, tweet_publisher

def create_twitter_tasks(topic: str, content_researcher, content_writer, tweet_publisher) -> List[Task]:
    research_task = Task(
        description=f"""Research the latest developments and important information about {topic}. 
        Focus on factual, valuable insights that would be worth sharing.""",
        expected_output="""A comprehensive but concise summary of the most relevant and 
        accurate information about the topic.""",
        agent=content_researcher
    )

    writing_task = Task(
        description=f"""Transform the research into a clear, professional tweet. 
        The tweet MUST:
        1. Start with exactly one ' prefix
        2. Be under 280 characters TOTAL
        3. Not be wrapped in quotes
        4. Not use hashtags
        5. Use at most one emoji if appropriate
        Focus on 1-2 key points only and be extremely concise.""",
        expected_output="""A clean, professional tweet that starts with a single ' prefix, 
        is under 280 characters total, has no quotes, and clearly communicates 
        1-2 key points without any excess.""",
        agent=content_writer
    )

    publishing_task = Task(
        description="""Review and if needed rewrite the tweet to ensure it meets all requirements:
        1. Starts with exactly one ' prefix (no duplicates)
        2. MUST be under 280 characters total
        3. Must NOT be wrapped in quotes
        4. Contains no hashtags
        5. Uses minimal emoji (max 1)
        6. Focuses on essential information only
        If any formatting issues exist, fix them while maintaining the key message.""",
        expected_output="""A final, polished tweet that meets ALL formatting requirements, 
        especially regarding the single prefix and no quotes, while effectively 
        communicating the core message.""",
        agent=tweet_publisher
    )

    return [research_task, writing_task, publishing_task]

def create_token_analysis_agents(token_service):
    """Create agents specialized in token analysis"""
    
    def get_token_info(token_address: str) -> str:
        """Get token info and handle the response"""
        if isinstance(token_address, str) and token_address.startswith('{'):
            import json
            data = json.loads(token_address)
            token_address = data.get('token_address')
        
        result = token_service.get_token_info(token_address)
        return str(result) if result else "No data found for token"

    # Create tool for token info
    token_tool = Tool(
        name="GetTokenInfo",
        func=get_token_info,
        description="Get detailed information about a token using its address. Input should be a token address string."
    )

    token_researcher = Agent(
        role='Token Research Analyst',
        goal='Analyze token data and extract key metrics',
        backstory="""You're a cryptocurrency analyst specializing in token metrics and market analysis. 
        You focus on providing accurate, data-driven insights about tokens, including price, liquidity, 
        market cap, and risk assessment.""",
        allow_delegation=False,
        tools=[token_tool],
        llm=ChatOpenAI(temperature=0.5, model="gpt-4"),
        verbose=True
    )

    market_analyst = Agent(
        role='Market Intelligence Specialist',
        goal='Analyze market dynamics and price movements',
        backstory="""You're a market intelligence specialist who excels at interpreting price movements, 
        liquidity patterns, and market trends. You provide clear insights about token performance and 
        market behavior.""",
        allow_delegation=False,
        tools=[token_tool],
        llm=ChatOpenAI(temperature=0.5, model="gpt-4")
    )

    risk_analyst = Agent(
        role='Risk Assessment Specialist',
        goal='Evaluate token risks and security aspects',
        backstory="""You're a risk assessment specialist who analyzes token security, identifies potential 
        risks, and evaluates the overall safety of tokens. You provide clear risk assessments and 
        security recommendations.""",
        allow_delegation=False,
        tools=[token_tool],
        llm=ChatOpenAI(temperature=0.5, model="gpt-4")
    )

    return token_researcher, market_analyst, risk_analyst

def create_token_tasks(token_address: str, token_researcher, market_analyst, risk_analyst) -> List[Task]:
    research_task = Task(
        description=f"""Analyze the token data for {token_address}. Focus on:
        1. Basic token information (name, symbol, decimals)
        2. Current market metrics (price in USD, market cap, supply)
        3. Pool information and liquidity
        4. Social media presence and creator information
        
        The data will be in this format:
        - token.name: Token name
        - token.symbol: Token symbol
        - token.decimals: Number of decimals
        - token.description: Token description
        - pools[0].price.usd: Current price in USD
        - pools[0].marketCap.usd: Market cap in USD
        - pools[0].liquidity.usd: Liquidity in USD
        - token.extensions: Social media links
        
        Provide a comprehensive but concise analysis of the token's fundamental metrics.""",
        expected_output="""A clear summary of the token's key metrics and characteristics, 
        including name, symbol, price, market cap, liquidity, and social presence.""",
        agent=token_researcher
    )

    market_task = Task(
        description=f"""Analyze the market performance data for {token_address}. Focus on:
        1. Price movements across timeframes (1h, 24h changes)
        2. Liquidity analysis from pools data
        3. Trading activity (buys, sells, transactions)
        4. Market trends from events data
        
        The data will include:
        - events.1h.priceChangePercentage: 1-hour price change
        - events.24h.priceChangePercentage: 24-hour price change
        - pools[0].liquidity: Pool liquidity data
        - buys/sells/txns: Trading activity metrics
        
        Provide clear insights about market behavior and performance.""",
        expected_output="""A detailed market analysis highlighting price movements, 
        liquidity status, trading activity, and key trends.""",
        agent=market_analyst
    )

    risk_task = Task(
        description=f"""Evaluate the security and risks for {token_address}. Focus on:
        1. Risk score and specific risk factors
        2. Security aspects from pools data (mint/freeze authority)
        3. Rug pull indicators
        4. Social media verification
        
        The data will include:
        - risk.score: Overall risk score
        - risk.risks: Array of specific risks
        - risk.rugged: Rug pull indicator
        - pools[0].security: Security authorities
        
        Provide a thorough risk assessment and security evaluation.""",
        expected_output="""A comprehensive risk analysis covering security aspects,
        specific risks identified, and overall safety assessment.""",
        agent=risk_analyst
    )

    return [research_task, market_task, risk_task] 