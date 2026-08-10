from telegram import Update
from telegram.constants import ChatAction
import random
import datetime
import requests
import asyncio

from slm_model import model_response

import logging
logger = logging.getLogger(__name__)

# start
async def start(update: Update, context):
	"""Sends a welcomer message when the command /start is issued."""
	user = update.effective_user
	await update.message.reply_html(
		f"🖖 Olá, {user.mention_html()}! Sou um bot de IA (Gemma3) rodando localmente em um Raspberry Pi 3.\nPosso tirar dúvida, agendar lembretes e trazer informações de clima.\n\nDigite /help para saber mais."
	)

# anwser
async def reponse(update: Update, context):
	"""Anwser user using Gemma3."""
	await update.message.reply_text("⏳ Pensando...")
	await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

	input_user = update.message.text
	ia_context = "Você é um assistente útil e conciso. Responda em Português"

	output_gemma = await asyncio.to_thread(
        model_response, 
        input=input_user, 
        cabecalho=ia_context
    )

	await update.message.reply_text(output_gemma)

# roll
async def roll(update: Update, context):
	"""Send a number between 1 - 6"""
	await update.message.reply_text(f"O número sorteado foi: {random.randint(1,6)}")

# time
async def get_time(update: Update, context):
	"""Tells the time"""
	await update.message.reply_text(f"São {datetime.datetime.now().strftime('%H:%M')}")

# help
async def help(update: Update, context):
	"""Send a help message."""
	await update.message.reply_text("Me mande uma pergunta e eu lhe respondo!\n\n"
	"Você também pode usar os seguintes comandos:\n"
	"/start - Iniciar o bot\n"
	"/help - Exibir esta mensagem de ajuda\n"
	"/alarm_min - Definir um lembrete que dispara em minutos (ex: /alarm_min 10 Ligue para sua mãe)\n"
	"/alarm_days - Definir um lembrete que dispara em dias (ex: /alarm_days 2 12:00 Compre leite)\n"
	"/city - Definir que cidade você se encontra\n"
	"/forecast - Trás informações diárias do clima.\nAcrescente 'yes'para receber atualizações todos os dias as 7:00 e 'no' para cancelar\n"
	"/status - retorna informações sobre o hardware"
	# "/facts - Obter um fato interessante em inglês\n"
	# "/dice - Sortear um número entre 1 e 6\n/time - Ver a hora atual\n"
	)

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
		await update.message.reply_text("Desculpe, não consegui buscar um fato agora. Tente novamente mais tarde.")