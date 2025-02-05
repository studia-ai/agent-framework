import os
import tweepy
from crewai import Crew, Task
from dotenv import load_dotenv
from tavily import TavilyClient
from studia_agent.tools import TwitterTools
from studia_agent.researcher import TokenAnalyzer
from studia_agent.agents import create_twitter_agents

# Load environment variables from .env
load_dotenv()

# Twitter API credentials from .env
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "")
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

# Add Tavily API key
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# Initialize Twitter client only if credentials are provided
twitter_client = None
if all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
    try:
        print("\nInitializing Twitter client...")
        print(f"API Key present: {bool(TWITTER_API_KEY)}")
        print(f"API Secret present: {bool(TWITTER_API_SECRET)}")
        print(f"Access Token present: {bool(TWITTER_ACCESS_TOKEN)}")
        print(f"Access Token Secret present: {bool(TWITTER_ACCESS_TOKEN_SECRET)}")
        
        # Initialize Twitter client with v2 API
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
            bearer_token=TWITTER_BEARER_TOKEN,
            wait_on_rate_limit=True
        )
        
        # Test if client is properly authenticated
        test_response = client.get_me()
        if test_response.data:
            print(f"Successfully authenticated as: @{test_response.data.username}")
            twitter_client = client
        else:
            print("Failed to authenticate with Twitter")
    except Exception as e:
        print(f"Error initializing Twitter client: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")

# Initialize Tavily client
tavily_client = None
if TAVILY_API_KEY:
    try:
        print("\nInitializing Tavily client...")
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        print("Successfully initialized Tavily client")
    except Exception as e:
        print(f"Error initializing Tavily client: {str(e)}")

def analyze_and_tweet_token(token_address: str):
    # First, analyze the token
    analyzer = TokenAnalyzer()
    analysis_result = analyzer.analyze_token(token_address)
    print("\nToken Analysis Results:")
    print(analysis_result)

    # Create a tweet about the analysis
    twitter_tools = TwitterTools(twitter_client)
    content_researcher, content_writer, tweet_publisher = create_twitter_agents(twitter_client)
    
    # Create specific task for token tweet
    token_tweet_task = Task(
        description=f"""Based on this token analysis, create an informative tweet about the token {token_address}.
        Include key metrics like price, market cap, and any significant findings.
        The tweet MUST:
        1. Start with exactly one ' prefix
        2. Be under 280 characters TOTAL
        3. Not be wrapped in quotes
        4. Not use hashtags
        5. Use at most one emoji if appropriate
        Analysis data: {analysis_result}""",
        expected_output="""A single tweet string that summarizes the token analysis, 
        formatted according to the requirements and under 280 characters.""",
        agent=content_writer
    )

    # Create crew for tweet creation
    crew = Crew(
        agents=[content_writer, tweet_publisher],
        tasks=[token_tweet_task],
        verbose=True
    )
    
    tweet_result = crew.kickoff()
    
    # Clean up and post the tweet
    tweet_content = str(tweet_result).strip()
    if tweet_content.startswith("'") and tweet_content.endswith("'"):
        tweet_content = tweet_content[1:-1].strip()
    
    print("\nAttempting to post tweet...")
    print(f"Tweet content: {tweet_content}")
    print(f"Tweet length: {len(tweet_content)} characters")
    
    post_result = twitter_tools.post_tweet(tweet_content)
    print(f"Tweet Result: {post_result}")
    
    return analysis_result, tweet_result

if __name__ == "__main__":
    # Studia token address
    STUDIA_TOKEN_ADDRESS = "2bz1pAVAWHk1qqtLx7oB5oy1PVQiQvtsqgaBbcqQpump"
    
    if twitter_client is None:
        print("Twitter client not initialized. Please check your credentials.")
    else:
        print(f"\nAnalyzing and tweeting about Studia token: {STUDIA_TOKEN_ADDRESS}")
        analysis_result, tweet_result = analyze_and_tweet_token(STUDIA_TOKEN_ADDRESS)
        print(f"\nAnalysis complete. Tweet result: {tweet_result}")

    # Example token address (replace with actual token address)
    token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC on Solana
    analysis_result, tweet_result = analyze_and_tweet_token(token_address)
