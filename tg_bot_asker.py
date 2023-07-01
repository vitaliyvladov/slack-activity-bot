from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import logging
import subprocess
import config

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = config.TELEGRAM_BOT_TOKEN

def start(update, context):
    keyboard = [
        [InlineKeyboardButton("Today", callback_data='today'),
         InlineKeyboardButton("Yesterday", callback_data='yesterday'),
         InlineKeyboardButton("All week", callback_data='week')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Choose period:', reply_markup=reply_markup)

def button(update, context):
    query = update.callback_query

    query.answer()

    subprocess.run(['python3', 'send_activity_report_to_telegram.py', query.data])

def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    # Create an Updater and pass your token to it.
    updater = Updater(TOKEN, use_context=True)

    # Get dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))

    # Logging for all errors
    dp.add_error_handler(error)

    # Start polling loop
    updater.start_polling()

    # Block until you terminate the bot (e.g. via Ctrl + C).
    updater.idle()

if __name__ == '__main__':
    main()
