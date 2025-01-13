import requests
from config import API_KEY

def search_nft(contract_address):
    url = f"https://api.unleashnfts.com/api/v2/nft/collection/metadata?sort_order=desc&offset=0&limit=30&contract_address={contract_address}"
    headers = {
        "accept": "application/json",
        "x-api-key": API_KEY
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None
