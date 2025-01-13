import requests

API_KEY = "316dd88ae8840897e1f61160265d1a3f"

def get_price_prediction(contract_address, token_id):
    url = f"https://api.unleashnfts.com/api/v2/nft/liquify/price_estimate?blockchain=ethereum&contract_address={contract_address}&token_id={token_id}"
    headers = {"accept": "application/json", "x-api-key": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["data"][0]
    return {"error": "Failed to fetch price prediction"}
