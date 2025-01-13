# wallet_profile_api.py

import requests
from config import API_KEY, BASE_URL

def get_wallet_profile(wallet_address):
    url = f"{BASE_URL}?wallet={wallet_address}&offset=0&limit=30"
    headers = {
        "accept": "application/json",
        "x-api-key": API_KEY
    }
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None
