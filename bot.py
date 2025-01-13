from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from collection_score import get_collection_score
from wallet_profile import get_wallet_profile
from price_prediction import get_price_prediction
from collection_metadata import search_nft
from config import TELEGRAM_TOKEN
import aiohttp

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Send me your wallet address.')

async def display_options(update_or_message, context: CallbackContext, clear_nft=False):
    if hasattr(update_or_message, 'effective_message'):
        message = update_or_message.effective_message
    elif hasattr(update_or_message, 'message'):
        message = update_or_message.message  # This is for callback queries
    else:
        message = update_or_message  # Assuming this is a direct Message object

    chat_id = message.chat_id
    
    if clear_nft:
        context.chat_data.pop('nft_contract_address', None)

    if 'wallet_address' not in context.chat_data:
        wallet_address = message.text
        context.chat_data['wallet_address'] = wallet_address

    keyboard = [
        [InlineKeyboardButton("Show Wallet Profile", callback_data="profile")],
        [InlineKeyboardButton("Search for NFTs", callback_data="ask_for_contract")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text='Choose an option:', reply_markup=reply_markup)

    

async def nft_details_menu(update_or_message, context: CallbackContext):
    # Determine if update_or_message is an Update or Message object
    if hasattr(update_or_message, 'effective_message'):
        message = update_or_message.effective_message
    elif hasattr(update_or_message, 'message'):
        message = update_or_message.message  # This is for callback queries
    else:
        message = update_or_message  # Assuming this is a direct Message object

    chat_id = message.chat_id
    keyboard = [
        [InlineKeyboardButton("Show Collection Metadata", callback_data="show_metadata")],
        [InlineKeyboardButton("Show Collection Score", callback_data="show_score")],
        [InlineKeyboardButton("Show Predicted Price", callback_data="show_price")],
        [InlineKeyboardButton("Check Anomaly", callback_data="check_anomaly")],
        [InlineKeyboardButton("Go Back", callback_data="go_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Ensure callback_query exists and use it to edit the message
    
    await context.bot.send_message(chat_id=chat_id, text='What would you like to do next?', reply_markup=reply_markup)

async def fetch_anomaly_prediction(features):
    url = "https://nft-nexus-g7co.onrender.com/anomaly-predict"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=features, headers={"Content-Type": "application/json"}) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {'prediction': 'Error with the prediction service'}
        except Exception as e:
            return {'prediction': f'An error occurred: {str(e)}'}


async def handle_query(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "profile":
        wallet_address = context.chat_data.get('wallet_address')
        print(wallet_address)
        if wallet_address:
            profile = get_wallet_profile(wallet_address)
            if profile and 'data' in profile and profile['data']:
                profile_data = profile['data'][0]
                nft_count = profile_data.get('nft_count', 'N/A')
                washtrade_nft_count = profile_data.get('washtrade_nft_count', 'N/A')
                marketplace_rewards = profile_data.get('nft_marketplace_reward', {})
                blur_rewards = marketplace_rewards.get('blur', 'N/A')
                looks_rewards = marketplace_rewards.get('looks', 'N/A')
                rari_rewards = marketplace_rewards.get('rari', 'N/A')

                message = (
                    f"NFT Count: {nft_count}\n"
                    f"Washtrade NFT Count: {washtrade_nft_count}\n"
                    "Marketplace Rewards:\n"
                    f" - Blur: {blur_rewards}\n"
                    f" - Looks: {looks_rewards}\n"
                    f" - Rari: {rari_rewards}"
                )
            else:
                message = "Failed to retrieve wallet profile or no data available."
        else:
            # Prompt user to send a wallet address if not found in context data
            message = "Please send your wallet address first."
        await query.message.reply_text(message)
    elif data == "ask_for_contract":
        await query.message.reply_text("Please send the contract address for the NFT collection.")
        context.chat_data['action'] = 'awaiting_contract'
    elif data == "show_metadata":
        chat_id = query.message.chat_id
        contract_address = context.chat_data.get('nft_contract_address')
        if contract_address:
            nft_info = search_nft(contract_address)
            if nft_info and 'data' in nft_info and nft_info['data']:
                nft_data = nft_info['data'][0]
                collection_name = nft_data.get('collection', 'N/A')
                description = nft_data.get('description', 'No description available.')
                image_url = nft_data.get('image_url', 'No image available.')
                discord_url = nft_data.get('discord_url', 'No Discord URL available.')
                external_url = nft_data.get('external_url', 'No website URL available.')
                instagram_url = nft_data.get('instagram_url', 'No Instagram URL available.')
                marketplace_url = nft_data.get('marketplace_url', 'No marketplace URL available.')
                medium_url = nft_data.get('medium_url', 'No Medium URL available.')
                twitter_url = nft_data.get('twitter_url', 'No Twitter URL available.')

                message = (
                    f"Collection Name: {collection_name}\n"
                    f"Description: {description}\n"
                    f"Image URL: {image_url}\n"
                    "Links:\n"
                    f" - Website: {external_url}\n"
                    f" - Marketplace: {marketplace_url}\n"
                    f" - Instagram: {instagram_url}\n"
                    f" - Discord: {discord_url}\n"
                    f" - Twitter: {twitter_url}\n"
                    f" - Medium: {medium_url}"
                )
            else:
                message = "Failed to retrieve NFT data or no data available."
        else:
            message = "No contract address found. Please search for NFTs first."
        await context.bot.send_message(chat_id=chat_id, text=message)
        await nft_details_menu(update.callback_query.message, context)
    elif data == "show_score":
        chat_id = query.message.chat_id
        contract_address = context.chat_data.get('nft_contract_address')
        if contract_address:
            # Fetch collection score data
            score_data = get_collection_score(contract_address)
            
            # Check if data is available and extract values
            if score_data and 'data' in score_data and score_data['data']:
                collection_data = score_data['data'][0]  # Access the first item in the data list
                
                # Extract required fields
                collection_score = collection_data.get('collection_score', 'N/A')
                fear_and_greed_index = collection_data.get('fear_and_greed_index', 'N/A')
                market_dominance_score = collection_data.get('market_dominance_score', 'N/A')

                # Construct the message
                message = f"Collection Score: {collection_score}\n" \
                    f"Fear and Greed Index: {fear_and_greed_index}\n" \
                    f"Market Dominance Score: {market_dominance_score}"
            else:
                message = "Failed to retrieve collection score or no data available."
        else:
            message = "No contract address found. Please search for NFTs first."

        # Use the correct attribute to reply to the user
        await context.bot.send_message(chat_id=chat_id, text=message)
        await nft_details_menu(update.callback_query.message, context)
       

    elif data == "check_anomaly":
        chat_id = query.message.chat_id
        contract_address = context.chat_data.get('nft_contract_address')
        if contract_address:
            score_data = get_collection_score(contract_address)
            if score_data and 'data' in score_data and score_data['data']:
                collection_data2 = score_data['data'][0]
                washtrade_index = collection_data2.get('washtrade_index', 'N/A')
                zero_profit_trades = collection_data2.get('zero_profit_trades', 'N/A')
                loss_making_volume = collection_data2.get('loss_making_volume', 'N/A')

                features = {
                    'washtrade_index': washtrade_index,
                    'zero_profit_trades': zero_profit_trades,
                    'loss_making_volume': loss_making_volume
                }
                prediction_result = await fetch_anomaly_prediction(features)
                message = f"Anomaly Prediction: {prediction_result.get('prediction', 'Unknown')}"
            else:
                message = "Failed to retrieve score data or no data available."
        else:
            message = "No contract address found. Please search for NFTs first."
    
        await context.bot.send_message(chat_id=chat_id, text=message)
        await nft_details_menu(update.callback_query.message, context)
        
    elif data == "show_price":
        await query.message.reply_text("Please send the token ID for price prediction.")
        context.chat_data['action'] = 'awaiting_token_id'
    elif data == "go_back":
        await display_options(query.message, context)

async def handle_message(update: Update, context: CallbackContext) -> None:
    action = context.chat_data.get('action')

    if action == 'awaiting_contract':
        contract_address = update.message.text
        context.chat_data['nft_contract_address'] = contract_address
        await nft_details_menu(update, context)
    elif action == 'awaiting_token_id':
        token_id = update.message.text
        contract_address = context.chat_data.get('nft_contract_address')
        if contract_address:
            price_data = get_price_prediction(contract_address, token_id)
            if (price_data):
                message = f"Price Estimate: {price_data['price_estimate']}\n" \
                        f"Lower Bound: {price_data['price_estimate_lower_bound']}\n" \
                        f"Upper Bound: {price_data['price_estimate_upper_bound']}"
            else:
                message = "Token Id not found"
        else:
            message = "No contract address found. Please search for NFTs first."
        await update.message.reply_text(message)
        await nft_details_menu(update, context)
    else:
        await display_options(update, context)

def main() -> None:
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
