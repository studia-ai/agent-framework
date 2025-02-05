import tweepy
from typing import Optional

class TwitterTools:
    def __init__(self, twitter_client=None):
        self.twitter_client = twitter_client


    def post_tweet(self, content: str) -> str:
        # Clean up the content first
        content = content.strip()
        
        # Remove any quotes
        content = content.replace('"', '').replace("'", "")
        
        # Check character limit (280 chars)
        if len(content) > 280:
            return f"Error: Tweet exceeds 280 characters (length: {len(content)}). Please rewrite to be more concise."
        
        if self.twitter_client is None:
            return f"[PREVIEW - No Twitter credentials] Tweet content: {content}"
        
        try:
            # Post tweet using v2 API
            response = self.twitter_client.create_tweet(text=content)
            tweet_id = response.data['id']
            return f"Tweet posted successfully! Tweet ID: {tweet_id}"
        except Exception as e:
            return f"Error posting tweet: {str(e)}" 

    def search_twitter(self, query: str, limit: Optional[int] = 10) -> str:
        """
        Search Twitter for recent tweets matching the query
        """
        if self.twitter_client is None:
            return f"[PREVIEW - No Twitter credentials] Would search Twitter for: {query}"
        
        try:
            # Search tweets using v2 API
            response = self.twitter_client.search_recent_tweets(
                query=query,
                max_results=min(limit, 100)  # API limit is 100
            )
            
            if not response.data:
                return "No tweets found matching your query."
                
            results = []
            for tweet in response.data:
                results.append(f"@{tweet.author_id}: {tweet.text}")
                
            return "\n\n".join(results)
            
        except Exception as e:
            return f"Error searching tweets: {str(e)}"