import aiohttp
import matplotlib.pyplot as plt
import io
from datetime import datetime
import ast



async def fetch_analytics(contract_address, time_range):
    url = f"https://api.unleashnfts.com/api/v2/nft/collection/analytics?blockchain=ethereum&contract_address={contract_address}&offset=0&limit=30&sort_by=sales&time_range={time_range}&sort_order=desc"
    headers = {
        "accept": "application/json",
        "x-api-key": "316dd88ae8840897e1f61160265d1a3f"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                
                return await response.json()
            else:
                return None  # You might want to handle different statuses and errors appropriately



async def plot_and_send_analytics(data, message):
    trends = {
        'assets_trend': 'Assets',
        'sales_trend': 'Sales',
        'transactions_trend': 'Transactions',
        'transfers_trend': 'Transfers',
        'volume_trend': 'Volume'
    }

    # Prepare and send a plot for each trend
    for trend_key, trend_name in trends.items():
        trend_data_raw = data['data'][0].get(trend_key, [])

        # Check if the data is in string format and convert if necessary
        if isinstance(trend_data_raw, str):
            trend_data = ast.literal_eval(trend_data_raw)
        else:
            trend_data = trend_data_raw

        dates = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S") for d in data['data'][0]['block_dates']]
        
        plt.figure(figsize=(10, 5))
        plt.plot(dates, trend_data, marker='o', linestyle='-', label=trend_name)
        plt.title(f'{trend_name} Trend Over Time')
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