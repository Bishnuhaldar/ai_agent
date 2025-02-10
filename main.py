import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import ReplyKeyboardMarkup
import streamlit as st
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

BOT_TOKEN = "7974533848:AAGH03VguQ_ue_3x2c0GpJHeaKGOJPD7AJk"

# Your existing async functions remain the same
async def echo(update: Update, context: CallbackContext):
    # ... your echo function code ...
    pass

async def user_info(update: Update, context: CallbackContext) -> None:
    # ... your user_info function code ...
    pass

async def start(update: Update, context: CallbackContext) -> None:
    # ... your start function code ...
    pass

def main():
    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(CommandHandler("info", user_info))
    
    st.write('bot is running....')
    
    # Run the bot in the background
    loop.create_task(app.run_polling())
    
    # Keep the script running
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
