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
import asyncio

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
		f"Olá, {user.mention_html()}! Eu sou um bot de eco, mas também posso lhe ajudar com algumas outras coisas.\n\nDigite /help para saber mais."
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
	"""Sets an alarm for a specified number of minutes."""
	try:
		minutes = int(context.args[0]) * 60
		label = " ".join(context.args[1:]) if len(context.args) > 1 else "Alarme"
		await update.message.reply_text(f"Lembrete: {label}.\nDefinido para {int(minutes/60)} minutos.")
		await asyncio.sleep(minutes) 
		await update.message.reply_text(f"Passaram-se {int(minutes/60)} minutos!\n{label}!")
	except (IndexError, ValueError):
		await update.message.reply_text("Uso: /alarm <minutos> <o que você quer lembrar> (ex: /alarm 10 Saia de casa)")

# help
async def help(update: Update, context):
	"""Send a help message."""
	await update.message.reply_text("Me mande uma mensagem e eu lhe retorno a mesma mensagem.\n\nVocê também pode usar os seguintes comandos:\n/start - Iniciar o bot\n/help - Exibir esta mensagem de ajuda\n/facts - Obter um fato interessante em inglês\n/dice - Sortear um número entre 1 e 6\n/time - Ver a hora atual\n/alarm - Definir um lembrete que dispara em minutos (ex: /alarm 10 Ligue para sua mãe)")
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


# add handlers
def add_handlers(app):
	app.add_handler(CommandHandler("start", start))
	app.add_handler(CommandHandler("help", help))
	app.add_handler(CommandHandler("facts", get_fact))
	app.add_handler(CommandHandler("dice", roll))
	app.add_handler(CommandHandler("time", get_time))
	app.add_handler(CommandHandler("alarm", alarm))
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# main
def main() -> None:
	TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

	if not TOKEN:
		raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")

	# Create the application and pass it back to your bot's token.
	app = Application.builder().token(TOKEN).build()

	# Register handlers
	add_handlers(app)

	# Run the bot until user presses Ctrl-C
	app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=="__main__":
	main()
