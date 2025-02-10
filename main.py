import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import ReplyKeyboardMarkup
import streamlit as st
from threading import Thread

# Apply nest_asyncio
nest_asyncio.apply()

# Store bot token in Streamlit secrets or environment variables for security
BOT_TOKEN = "7974533848:AAGH03VguQ_ue_3x2c0GpJHeaKGOJPD7AJk"

async def echo(update: Update, context: CallbackContext):
    user_message = update.message.text
    user = update.message.from_user
    
    if (str.lower('how') in user_message.lower()) or (str.lower('echo') in user_message.lower()):
        try:
            await update.message.reply_photo('wallpaperflare.com_wallpaper (1).jpg', caption='Here is the image')
        except:
            await update.message.reply_text("Sorry, couldn't send the image")
    
    if user.first_name.lower() == 'karan':
        await update.message.reply_text('Tu karan hain')
    if user.first_name.lower() == 'bishnu':
        await update.message.reply_text('bishnu bhai namaste')

async def user_info(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    await update.message.reply_text(f"Hello {user.first_name}! Your ID is {user.id}.")

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        ["Help", "kunjo"],
        ["About", 'Dubai']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

def run_bot():
    # Create and set event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Initialize bot application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(CommandHandler("info", user_info))
    
    # Start the bot
    app.run_polling()

# Streamlit UI
st.title("Telegram Bot Control Panel")

# Bot status tracking
if 'bot_running' not in st.session_state:
    st.session_state.bot_running = False

# Start/Stop button
if not st.session_state.bot_running:
    if st.button("Start Bot"):
        st.write('Starting bot...')
        bot_thread = Thread(target=run_bot)
        bot_thread.start()
        st.session_state.bot_running = True
        st.write('Bot is running! You can now interact with it on Telegram.')
        st.write('Available commands:')
        st.write('- /start : Shows the main menu')
        st.write('- /info : Shows your user information')
else:
    st.write('Bot is currently running!')
    st.write('To stop the bot, please restart the Streamlit app.')

# Instructions
st.markdown("""
## How to use the bot
1. Start a chat with your bot on Telegram
2. Click the Start Bot button above
3. Use the following commands in Telegram:
   - `/start` to see the main menu
   - `/info` to see your user information
   - Send any message to test the echo functionality
""")

# Add some basic error handling
try:
    if st.session_state.bot_running:
        st.info("Bot is active and listening for messages on Telegram")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.session_state.bot_running = False
