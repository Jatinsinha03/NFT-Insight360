import requests

API_KEY = "316dd88ae8840897e1f61160265d1a3f"
BASE_URL = "https://api.unleashnfts.com/api/v2/nft/collection/profile"

def get_collection_score(contract_address):
    print(contract_address)
    url = f"https://api.unleashnfts.com/api/v2/nft/collection/profile?blockchain=ethereum&contract_address={contract_address}&time_range=all&offset=0&limit=30&sort_by=washtrade_index&sort_order=desc"
    headers = {"accept": "application/json", "x-api-key": API_KEY}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to fetch collection score"}
