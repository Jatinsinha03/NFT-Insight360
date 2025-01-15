import requests
import ast
from datetime import datetime
import matplotlib.pyplot as plt
import io

def fetch_washtrade_data(contract_address, time_range):
    """Fetch washtrade data from the API."""
    url = f"https://api.unleashnfts.com/api/v2/nft/collection/washtrade?blockchain=ethereum&contract_address={contract_address}&time_range={time_range}&offset=0&limit=30&sort_by=washtrade_assets&sort_order=desc"
    headers = {
        "accept": "application/json",
        "x-api-key": "316dd88ae8840897e1f61160265d1a3f"
    }

    response = requests.get(url, headers=headers)
    return response.json()

def parse_trend_data(data, trend_key):
    """Parse the trend data from the API response."""
    raw_trend_data = data['data'][0][trend_key]
    if isinstance(raw_trend_data, str):
        trend_data = ast.literal_eval(raw_trend_data)
    else:
        trend_data = raw_trend_data
    block_dates = [datetime.strptime(date.strip(" '\""), "%Y-%m-%d %H:%M:%S") for date in data['data'][0]['block_dates']]
    return trend_data, block_dates

def plot_trend(trend_data, dates, trend_name):
    """Generate a plot from trend data."""
    plt.figure(figsize=(10, 5))
    plt.plot(dates, trend_data, marker='o', linestyle='-', label=trend_name)
    plt.title(trend_name)
    plt.xlabel('Date and Time')
    plt.ylabel('Counts')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

async def display_washtrade_trends(message, contract_address, trend_key, time_range):
    """Fetch, parse, and display a specific washtrade trend."""
    data = fetch_washtrade_data(contract_address, time_range)
    if 'data' in data and data['data']:
        # Extract trend data for the specific trend_key
        if trend_key in data['data'][0]:
            trend_data, dates = parse_trend_data(data, trend_key)
            buf = plot_trend(trend_data, dates, trend_key.replace('_', ' ').title())
            await message.reply_photo(photo=buf)
            buf.close()
        else:
            await message.reply_text(f"No data available for {trend_key.replace('_', ' ').title()}.")
    else:
        await message.reply_text("Failed to retrieve washtrade trend data.")
