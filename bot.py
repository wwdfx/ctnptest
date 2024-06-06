import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = '7341839121:AAG1JkFiDXf2x-fZ60prFXgbjKGJJ0I3ATY'
NOVA_POSHTA_API_URL = 'https://api.novaposhta.ua/v2.0/json/'

# Function to check tracking status
async def check_tracking_status(tracking_number):
    payload = {
        "apiKey": "36c858e271ba589b36d7c269004d3306",
        "modelName": "TrackingDocument",
        "calledMethod": "getStatusDocuments",
        "methodProperties": {
            "Documents": [
                {"DocumentNumber": tracking_number}
            ]
        }
    }
    response = requests.post(NOVA_POSHTA_API_URL, json=payload)
    data = response.json()
    
    if data['success']:
        status = data['data'][0]['Status']
        return status
    else:
        return None

# Function to handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    tracking_pattern = re.compile(r'20400\d{9}')
    match = tracking_pattern.search(message_text)
    
    if match:
        tracking_number = match.group(0)
        status = await check_tracking_status(tracking_number)
        
        if status == "Прибув у відділення":
            response_text = f"ТТН: {tracking_number} на відділенні."
            await context.bot.send_message(chat_id=update.message.chat_id, text=response_text, reply_to_message_id=update.message.message_id)

# Main function to start the bot
def main():
    # Initialize the bot and add handlers
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add a message handler to process group messages
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    app.add_handler(message_handler)
    
    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    main()

    