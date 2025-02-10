from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram import ReplyKeyboardMarkup
import streamlit as st


# Replace with your actual bot token
BOT_TOKEN = "7974533848:AAGH03VguQ_ue_3x2c0GpJHeaKGOJPD7AJk"


# async def start(update: Update, context: CallbackContext):
#     await update.message.reply_text("Hello! I am your bot. Send me a message!")

async def echo(update: Update, context: CallbackContext):
    user_message = update.message.text
    user = update.message.from_user
    # await update.message.reply_text(f"{user_message}")
    if (str.lower('how') in user_message.lower()) or (str.lower('echo') in user_message.lower()):
        # await update.message.reply_text('Im fine, tumi kamon accho')
        
        await update.message.reply_photo('wallpaperflare.com_wallpaper (1).jpg',caption='Here is teh image')

    # if(str.lower('Kunjo') in user_message.lower()):
    #     for i in range(20):
    #         await update.message.reply_text('')
    if user.first_name.lower()=='karan':
        await update.message.reply_text('Tu karan hain')

    if user.first_name.lower()=='bishnu':
        await update.message.reply_text('bishnu bhai namaste ')
    
        
        # await update.message.reply_photo('wallpaperflare.com_wallpaper (1).jpg',caption='Here is teh image')

async def user_info(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    await update.message.reply_text(f"Hello {user.first_name}! Your ID is {user.id}. and {update}")


async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [["Help", "kunjo"], ["About",'Dubai']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("Choose an option:", reply_markup=reply_markup)

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    app.add_handler(CommandHandler("info",user_info))

    st.write('bot is running....')
    app.run_polling()

if __name__ == "__main__":
    main()
