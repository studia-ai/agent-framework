import os
import requests
from dotenv import load_dotenv

def test_token_api():
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("SOLANA_TRACKER_API_KEY")
    print(f"API Key: {api_key}")
    if api_key:
        print(f"API Key present: {api_key[:8]}...")
    else:
        print("No API key found!")
        return
    
    # API configuration
    base_url = "https://data.solanatracker.io"
    token_address = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
    
    # Set up headers
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json"
    }
    
    print(f"\nTesting with token address: {token_address}")
    print(f"URL: {base_url}/tokens/{token_address}")
    print(f"Headers: {headers}")
    
    try:
        response = requests.get(
            f"{base_url}/tokens/{token_address}",
            headers=headers
        )
        
        # Print status code
        print(f"\nStatus Code: {response.status_code}")
        
        # If there's an error, print the error message
        if response.status_code != 200:
            print(f"Error Response: {response.text}")
            return
        
        # Parse and print the response
        result = response.json()
        print("\nAPI call successful!")
        if result.get('token'):
            print(f"Token name: {result['token'].get('name')}")
            print(f"Token symbol: {result['token'].get('symbol')}")
        print("\nFull response:")
        print(result)
        
    except requests.RequestException as e:
        print(f"Error making request: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")

if __name__ == "__main__":
    test_token_api() 