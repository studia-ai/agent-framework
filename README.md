# Studia Agent Framework 🤖

[Follow us on Twitter](https://x.com/StudiaAI)

## Official Launch: 2bz1pAVAWHk1qqtLx7oB5oy1PVQiQvtsqgaBbcqQpump

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/studia-ai/agent-framework.git
cd agent-framework

# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Set up your environment variables
cp .env.example .env

# Required API Keys
# Make sure to add the following keys to your .env file:
# SOLANA_TRACKER_API_KEY=<your_sol_tracker_api_key>
# TWITTER_API_KEY=<your_twitter_api_key>
# TWITTER_API_SECRET=<your_twitter_api_secret>
# TWITTER_ACCESS_TOKEN=<your_twitter_access_token>
# TWITTER_ACCESS_TOKEN_SECRET=<your_twitter_access_token_secret>
# TWITTER_BEARER_TOKEN=<your_twitter_bearer_token>
# TAVILY_API_KEY=<your_tavily_api_key>

# Run the project
poetry run python src/studia_agent/main.py
```

## 📚 Additional Resources
- [Tavily Documentation](https://docs.tavily.com/docs/gpt-researcher/getting-started)
- [Solana Tracker API Documentation](https://docs.solanatracker.io/public-data-api/docs)
