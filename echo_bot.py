# Tutorial Echo Bot: https://teleclaw.bot/blog/telegram-bot-python-tutorial

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import logging
import os

# Fetch Token via env
load_dotenv()

# Enable logging
logging.basicConfig(
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	level=logging.INFO
)
logger = logging.getLogger(__name__)


# Handlers: functions that process incoming updates
# start
async def start(update: Update, context):
	"""Sends a welcomer message when the command /start is issued."""
	user = update.effective_user
	await update.message.reply_html(
		f"Saudações {user.mention_html()}! Este que vos fala se entitula como um androide de interlocução pleonástica! Conte-me algo ou digite /help para ajuda...",
		# reply_markup=ForceReply(selective=True),
		# # Optional: force reply to this message
	)

# echo
async def echo(update: Update, context):
	"""Echoes the user message."""
	await update.message.reply_text(update.message.text)


# help
async def help(update: Update, context):
	"""Send a help message."""
	await update.message.reply_text("Diga-me quaisquer pensamento, seja este frívolo ou pujante, e eu ecoá-lo-ei!")

# main
def main() -> None:
	TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

	if not TOKEN:
		raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")

	# Create the application and pass it back to your bot's token.
	app = Application.builder().token(TOKEN).build()

	# Register handlers
	app.add_handler(CommandHandler("start", start))
	app.add_handler(CommandHandler("help", help))
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

	# Run the bot until user presses Ctrl-C
	app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=="__main__":
	main()
