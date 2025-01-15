import requests
import ast
from datetime import datetime
import matplotlib.pyplot as plt
import io
from aiogram import types

async def fetch_trader_data(contract_address, trend_type, time_range):
    url = f"https://api.unleashnfts.com/api/v2/nft/collection/traders?blockchain=ethereum&contract_address={contract_address}&offset=0&limit=30&sort_by=traders&time_range={time_range}&sort_order=desc"
    headers = {
        "accept": "application/json",
        "x-api-key": "316dd88ae8840897e1f61160265d1a3f"
    }

    response = requests.get(url, headers=headers)
    return response.json()

def parse_trend_data(data, trend_type):
    # Parse trend data and dates, handling string-lists correctly
    raw_trend_data = data['data'][0].get(trend_type, '[]')
    
    # Check if the raw_trend_data is a string that needs to be converted into a list
    if isinstance(raw_trend_data, str):
        try:
            trend_data = ast.literal_eval(raw_trend_data)
        except ValueError as e:
            print(f"Error parsing string: {e}")
            trend_data = []  # default to an empty list in case of parsing error
    else:
        trend_data = raw_trend_data 
    block_dates = [datetime.strptime(date.strip(" '\""), "%Y-%m-%d %H:%M:%S") for date in data['data'][0]['block_dates']]
    return trend_data, block_dates

def plot_trend(trend_data, block_dates, trend_name):
    plt.figure(figsize=(10, 5))
    plt.plot(block_dates, trend_data, marker='o', linestyle='-', label=trend_name)
    plt.title(f"{trend_name} over Time")
    plt.xlabel('Date and Time')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

async def display_trader_trend(message: types.Message, contract_address, trend_type, time_range):
    data = await fetch_trader_data(contract_address, trend_type, time_range)
    if 'data' in data and data['data']:
        trend_data, block_dates = parse_trend_data(data, trend_type)
        buf = plot_trend(trend_data, block_dates, trend_type.replace('_', ' ').title())
        await message.reply_photo(photo=buf)
        buf.close()
    else:
        await message.reply_text("Failed to retrieve trader trend data.")

