import aiohttp
import matplotlib.pyplot as plt
import io
from datetime import datetime
import ast

async def fetch_market_price_trends(contract_address, time_range):
    url = f"https://api.unleashnfts.com/api/v2/nft/collection/scores?blockchain=ethereum&contract_address={contract_address}&time_range={time_range}&offset=0&limit=30&sort_by=market_cap&sort_order=desc"
    headers = {
        "accept": "application/json",
        "x-api-key": "316dd88ae8840897e1f61160265d1a3f"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

async def plot_trends(data, message):
    if not data or 'data' not in data or not data['data']:
        await message.reply_text("No trend data available.")
        return

    trends = {
        'marketcap_trend': 'Market Cap Trend',
        'price_ceiling_trend': 'Price Ceiling Trend'
    }

    # Assuming 'market_cap' and 'price_ceiling' are at the same level as 'data'
    market_cap = data['data'][0].get('market_cap', 'Not Available')
    price_ceiling = data['data'][0].get('price_ceiling', 'Not Available')
    mpc_info = f"Market Cap: {market_cap}\nPrice Ceiling: {price_ceiling}"
    
    for trend_key, trend_name in trends.items():
        # Fetch and evaluate the trend data if it's a string (assumed to be list-like)
        raw_trend_data = data['data'][0].get(trend_key, '[]')
        if isinstance(raw_trend_data, str):
            trend_data = ast.literal_eval(raw_trend_data)
        else:
            trend_data = raw_trend_data

        # Handle date strings that might have extra quotes
        date_strings = data['data'][0].get('block_dates', [])
        cleaned_dates = [d.strip(" '\"") for d in date_strings]  # Strip extra quotes and spaces
        dates = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S") for d in cleaned_dates]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, trend_data, marker='o', linestyle='-', label=trend_name)
        plt.title(trend_name)
        plt.xlabel('Date and Time')
        plt.ylabel(trend_name)
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()

        await message.reply_photo(photo=buf)
        buf.close()

    # Send market cap and price ceiling info after plotting trends
    await message.reply_text(mpc_info)