from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import logging
import os
import requests
import sys
import time
import random
import datetime

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
		f"Saudações, {user.mention_html()}! Este que vos fala se entitula como um andróide de interlocução pleonástica! Conte-me algo ou digite /help para ajuda...",
		# reply_markup=ForceReply(selective=True),
		# # Optional: force reply to this message
	)

# echo
async def echo(update: Update, context):
	"""Echoes the user message."""
	await update.message.reply_text(update.message.text)

# roll
async def roll(update: Update, context):
	"""Send a number between 1 - 6"""
	await update.message.reply_text(f"O número sorteado foi: {random.randint(1,6)}")

# time
async def get_time(update: Update, context):
	"""Tells the time"""
	await update.message.reply_text(f"São {datetime.datetime.now().strftime('%H:%M')}")

# alarm
async def alarm(update: Update, context):
	"""Sets an alarm for a specified number of seconds."""
	try:
		seconds = int(context.args[0])
		await update.message.reply_text(f"Alarme definido para {seconds} segundos.")
		time.sleep(seconds)
		await update.message.reply_text(f"Alarme de {seconds} segundos! O tempo acabou!")
	except (IndexError, ValueError):
		await update.message.reply_text("Uso: /alarm <segundos>")

# help
async def help(update: Update, context):
	"""Send a help message."""
	await update.message.reply_text("Diga-me quaisquer pensamento, seja este frívolo ou pujante, e eu ecoá-lo-ei! Se não souber o que espressar, me peça /facts e aprenda algo novo em inglês, /dice para sortear um número de 1 a 6 ou /time para saber as horas.")
# facts
async def get_fact(update: Update, context):
	"""Fetch a random fact from an external API."""
	try:
		resp = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
		resp.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
		fact_data = resp.json()
		await update.message.reply_text(f"Did you know? {fact_data['text']}")
	except requests.exceptions.RequestException as e:
		logger.error(f"Erro ao buscar um fato: {e}")
		await update.message.reply_text("Deculpe, eu não consegui buscar um fato agora. Tente novamente mais tarde.")



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
	app.add_handler(CommandHandler("facts", get_fact))
	app.add_handler(CommandHandler("dice", roll))
	app.add_handler(CommandHandler("time", get_time))
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

	# Run the bot until user presses Ctrl-C
	app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=="__main__":
	main()
