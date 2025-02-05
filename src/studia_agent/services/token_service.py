import os
import requests
from typing import Dict, Any, Optional

class TokenService:
    def __init__(self):
        self.base_url = "https://data.solanatracker.io"
        self.api_key = os.getenv("SOLANA_TRACKER_API_KEY")
        
    def get_token_info(self, token_address: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve information for a specific token from the Solana Tracker API.
        
        Args:
            token_address (str): The address of the token
            
        Returns:
            dict: Token information including market data, pools, risks, etc.
        """
        try:
            # Handle case where input might be a JSON string
            if isinstance(token_address, str) and token_address.startswith('{'):
                import json
                data = json.loads(token_address)
                token_address = data.get('token_address')

            headers = {
                "x-api-key": self.api_key,
                "Accept": "application/json"
            }
            
            print(f"Fetching data for token: {token_address}")  # Debug print
            response = requests.get(
                f"{self.base_url}/tokens/{token_address}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            print(f"API Response: {data}")  # Debug print
            return data
            
        except requests.RequestException as e:
            print(f"Error fetching token info: {str(e)}")
            return None 