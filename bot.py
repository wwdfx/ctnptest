import re
import requests
import schedule
import time
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = '7341839121:AAG1JkFiDXf2x-fZ60prFXgbjKGJJ0I3ATY'
NOVA_POSHTA_API_URL = 'https://api.novaposhta.ua/v2.0/json/'

# Dictionary to store messages with tracking numbers
messages_to_check = {}

# Function to check tracking status
async def check_tracking_status(tracking_number):
    payload = {
        "apiKey": "YOUR_NOVA_POSHTA_API_KEY",
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
        
        # Store the message for periodic checks
        messages_to_check[tracking_number] = update.message

# Periodic check function
async def periodic_check(context: ContextTypes.DEFAULT_TYPE):
    current_time = datetime.now().strftime('%H:%M')
    if current_time in ['12:00', '14:00', '16:00', '18:30']:
        for tracking_number, message in messages_to_check.items():
            status = await check_tracking_status(tracking_number)
            if current_time == '18:30' and status != "Прибув у відділення":
                response_text = f"ТТН: {tracking_number} статус: {status}"
                await context.bot.send_message(chat_id=message.chat_id, text=response_text, reply_to_message_id=message.message_id)

# Function to run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Main function to start the bot
def main():
    # Initialize the bot and add handlers
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add a message handler to process group messages
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    app.add_handler(message_handler)

    # Schedule the periodic checks
    schedule.every().day.at("12:00").do(lambda: asyncio.run(periodic_check(app)))
    schedule.every().day.at("14:00").do(lambda: asyncio.run(periodic_check(app)))
    schedule.every().day.at("16:00").do(lambda: asyncio.run(periodic_check(app)))
    schedule.every().day.at("18:30").do(lambda: asyncio.run(periodic_check(app)))

    # Start the scheduler in a separate thread
    from threading import Thread
    scheduler_thread = Thread(target=run_scheduler)
    scheduler_thread.start()

    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    main()

