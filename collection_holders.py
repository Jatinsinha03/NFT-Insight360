import aiohttp
import matplotlib.pyplot as plt
import io
import ast

async def fetch_holder_data(contract_address):
    url = f"https://api.unleashnfts.com/api/v2/nft/collection/holders?blockchain=ethereum&contract_address={contract_address}&time_range=24h&offset=0&limit=30&sort_by=holders&sort_order=desc"
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

async def plot_holder_trend(data, message):
    holder_trend = ast.literal_eval(data['total_holder_trend'])
    dates = data['block_dates']

    plt.figure(figsize=(10, 5))
    plt.plot(dates, holder_trend, marker='o', linestyle='-')
    plt.title('Holder Trend Over Time')
    plt.xlabel('Date and Time')
    plt.ylabel('Number of Holders')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()

    await message.reply_photo(photo=buf)
    buf.close()
    # Also display basic holder info
    holder_info = f"Holders: {data['holders']}\nChange: {data['holders_change']}"
    await message.reply_text(holder_info)
