from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import logging
import os
import requests
import random
import datetime
import json
import openmeteo_requests
import requests_cache
from retry_requests import retry

# Fetch Token via env
load_dotenv()

# Enable logging
logging.basicConfig(
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
	level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
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

# alarm callback
async def _alarm_callback(context):
	"""Callback function to send the alarm message."""
	job = context.job
	await context.bot.send_message(job.chat_id, text=f"Lembre-se!\n{job.data}")

# alarm minutes
async def alarm_min(update: Update, context):
	"""Sets an alarm for a specified number of minutes."""
	try:
		total_seconds = int(context.args[0]) * 60
		label = " ".join(context.args[1:]) if len(context.args) > 1 else "Alarme"

		chat_id = update.effective_chat.id # Get the user's chat ID
		context.job_queue.run_once(
			_alarm_callback,
			total_seconds,
			chat_id=chat_id,
			data=label
		)
		await update.message.reply_text(f"Lembrete: {label}.\nDefinido para {int(total_seconds/60)} minutos.")

	except (IndexError, ValueError):
		await update.message.reply_text("Uso: /alarm_min <minutos> <o que você quer lembrar> (ex: /alarm 10 Saia de casa)")

# alarm days
async def alarm_days(update: Update, context):
	"""Sets an alarm for a specified number of days."""
	try:
		now = datetime.datetime.now()
		days = int(context.args[0])
		hour, minute = map(int, context.args[1].split(':'))
		future_day = now + datetime.timedelta(days=days) # Calculate the future date
		alarm_time = future_day.replace(hour=hour, minute=minute, second=0, microsecond=0) # Calculate the exact alarm time
		total_seconds = int((alarm_time - now).total_seconds()) # Calculate the total seconds until the alarm
		label = " ".join(context.args[2:]) if len(context.args) > 2 else "Alarme"

		if total_seconds <= 0:
			await update.message.reply_text("O horário definido já passou. Por favor, defina um horário futuro.")
			return

		chat_id = update.effective_chat.id # Get the user's chat ID
		context.job_queue.run_once(
			_alarm_callback, # which function to call when the job is run
			total_seconds, # when to run the job (in seconds)
			chat_id=chat_id, # which chat to send the message to
			data=label # what message to send when the job is run
		)

		await update.message.reply_text(f"Lembrete: {label}.\nDefinido para daqui {days} dias às {hour:02d}:{minute:02d}.")
	except (IndexError, ValueError):
		await update.message.reply_text("Uso: /alarm <dias> <horário em 24h> <o que você quer lembrar>\n"
		"(ex: /alarm_days 2 11:30 Volte para a academia)\n Agendará um lembrete para daqui a 2 dias às 11:30.")

# help
async def help(update: Update, context):
	"""Send a help message."""
	await update.message.reply_text("Me mande uma mensagem e eu lhe retorno a mesma mensagem.\n\n" \
	"Você também pode usar os seguintes comandos:\n/start - Iniciar o bot\n/help - Exibir esta mensagem de ajuda\n"
	"/facts - Obter um fato interessante em inglês\n/dice - Sortear um número entre 1 e 6\n/time - Ver a hora atual\n"
	"/alarm_min - Definir um lembrete que dispara em minutos (ex: /alarm_min 10 Ligue para sua mãe)\n"
	"/alarm_days - Definir um lembrete que dispara em dias (ex: /alarm_days 2 12:00 Compre leite)")

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

# city persistence
async def city(update: Update, context):
	"""Saves or print the city name"""
	if len(context.args) < 1:
		try: 
			with open('user_info.json') as file: # 'with' closes the file without the need of file.close() command
				user_info = json.load(file)
		except FileNotFoundError:
			user_info = {} # creates missing dic

		if 'city' in user_info:
			city = user_info['city']
			await update.message.reply_text(f"A cidade escolhida para as notificações de tempo é {city}." \
			"\nPara atualizar a cidade escreva /city <nome da cidade>.")
		else:
			await update.message.reply_text("Sem cidade determinada para as atualizações do tempo." \
			"\nPara escolher a cidade escreva /city <nome da cidade>.")
	else:
		try:
			city = " ".join(context.args)
			resp = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                    params={"name": city, "count": 1, "language": "pt"})
			resp.raise_for_status()
			resp_data = resp.json()

			lat = resp_data['results'][0]["latitude"]
			lon = resp_data['results'][0]["longitude"]
			tz = resp_data['results'][0]["timezone"]
			user_info = {'city' : city, 'lat' : lat, 'lon' : lon, 'tz': tz}

			with open('user_info.json', 'w') as file:
				json.dump(user_info, file)
			await update.message.reply_text(f"Cidade atualizada para {city}.\nLatitude = {lat}\nlongitude = {lon}")
		except requests.exceptions.RequestException as e:
				logger.error(f"Erro ao buscar latitude e longitude: {e}")
				await update.message.reply_text("Desculpe, não consegui atualizar sua cidade agora. Tente novamente mais tarde.")

# city forecast
async def forecast(update: Update, context):
	"""Fetch city forecast information via open meteo API"""
	try: 
		with open('user_info.json') as file:
			user_info = json.load(file)
		
		city = user_info['city']
		lat = user_info['lat']
		lon = user_info['lon']
		tz = user_info['tz']

		# Setup the Open-Meteo API client with cache and retry on error
		cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
		retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
		openmeteo = openmeteo_requests.Client(session = retry_session)

		url = "https://api.open-meteo.com/v1/forecast"
		params = {
			"latitude": lat,
			"longitude": lon,
			"daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
			"timezone": tz,
			"forecast_days": 1,
		}

		responses = openmeteo.weather_api(url, params = params)
		resp = responses[0]
		daily = resp.Daily()
		temp_max = daily.Variables(0)
		temp_min = daily.Variables(1)
		precipitation_prob = daily.Variables(2)

		await update.message.reply_text(f"Hoje {city} terá a máxima de {temp_max} e a mínima de {temp_min},\ncom chance máxima de precipitação de {precipitation_prob}.")
		
	except FileNotFoundError:
		await update.message.reply_text("Utilize o comando /city para registrar a cidade que você deseja informações de clima.")

# add handlers
def add_handlers(app):
	app.add_handler(CommandHandler("start", start))
	app.add_handler(CommandHandler("help", help))
	app.add_handler(CommandHandler("facts", get_fact))
	app.add_handler(CommandHandler("dice", roll))
	app.add_handler(CommandHandler("time", get_time))
	app.add_handler(CommandHandler("alarm_min", alarm_min))
	app.add_handler(CommandHandler("alarm_days", alarm_days))
	app.add_handler(CommandHandler("city", city))
	app.add_handler(CommandHandler("forecast", forecast))
	app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# main
def main() -> None:
	# Token verification
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
