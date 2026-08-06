from telegram import Update
import requests
import datetime
import json
from zoneinfo import ZoneInfo

from persistence import load_user_info, save_user_info

import logging
logger = logging.getLogger(__name__)

# forecast callback
async def _forecast_callback(context):
	"""Callback function to send the forecast message."""
	job = context.job
	user_info = job.data

	message = await _forecast_message(user_info)
	await context.bot.send_message(job.chat_id, text=f"🌞 Bom dia! Aqui está a previsão de hoje:\n\n{message}")

# fetch forecast info
async def _forecast_message(user_info):
	"""Fetch city forecast information via open meteo API"""
	city = user_info['city']
	lat = user_info['lat']
	lon = user_info['lon']
	timezone = user_info['tz']
	
	url = "https://api.open-meteo.com/v1/forecast"
	params = {
			"latitude": lat,
			"longitude": lon,
			"daily": ["weather_code","temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
			"timezone": timezone,
			"forecast_days": 1,
	}
	responses = requests.get(url, params = params)
	resp = responses.json()
	
	temp_max = resp["daily"]["temperature_2m_max"][0]
	temp_min = resp["daily"]["temperature_2m_min"][0]
	rain = resp["daily"]["precipitation_probability_max"][0]
	code = resp["daily"]["weather_code"][0]

	# rain message
	if rain >= 60:
		rain_message = f"\n\nChances de chuva de {rain}%. Não esqueça do guarda chuva!"
	elif rain >= 30:
		rain_message = f"\n\nChances de chuva de {rain}%."
	else:
		rain_message = f"\n\nChances baixas de chuva: {rain}%."

	# weather code message
	match code:
		case 0:
			code_message = "☀️ Dia ensolarado "
		case 1 | 2 | 3:
			code_message = "🌤️ Dia parcialmente nublado "
		case 45 | 48:
			code_message = "🌬️ Dia enevoado "
		case 51 | 53 | 55:
			code_message = "☁️ Dia nublado "
		case 56 | 57:
			code_message = "🌧️ Dia de garoa "
		case 61 | 63 | 65 | 80 | 81:
			code_message = "🌧️ Dia de chuva "
		case 66 | 67 | 82:
			code_message = "⛈️ Dia de chuva intensa "
		case 71 | 73 | 75 | 77 | 85 | 86:
			code_message = "❄️ Dia de neve (👀 oxe???) "
	
	return(code_message + f"hoje em {city}.\nMáxima de {temp_max}°C e mínima de {temp_min}°C." + rain_message)

# forecast updates
async def forecast(update: Update, context):
	"""handle user info for forecast and updates notify"""
	job_name = "forecast"

	user_info = load_user_info()
	if not user_info.get('city'):
		await update.message.reply_text("Utilize o comando /city para registrar a cidade que você deseja informações de clima.")
		return

	if len(context.args) < 1:
		text = await _forecast_message(user_info)
		await update.message.reply_text(text)

	elif context.args[0].lower() == "yes":
		chat_id = update.effective_chat.id

		user_info['notify'] = True
		user_info['chat_id'] = chat_id

		save_user_info(user_info)
		schedule_forecast(context.job_queue, chat_id, user_info)

		await update.message.reply_text(f"Atualizações diárias ativadas! Você receberá a previsão todos os dias às 07:00 (Horário de {user_info['tz']}).")

	elif context.args[0].lower() == "no":
		user_info['notify'] = False
		save_user_info(user_info)

		# cancela o agendamento
		current_jobs = context.job_queue.get_jobs_by_name(job_name)
		for job in current_jobs:
			job.schedule_removal()

		await update.message.reply_text("Atualizações diárias de clima desativadas.")

# reschedule forecast
def reschedule_forecast(app):

	user_info = load_user_info()
	if not user_info:
		return

	if user_info.get('notify') and user_info.get('chat_id') and user_info.get('tz'): # .get retorna o valor ou null -> não quebra
		schedule_forecast(app.job_queue, user_info['chat_id'], user_info)

# schedule on job queue
def schedule_forecast(job_queue, job_name, chat_id, user_info):
	# remove agendamentos anteriores
	current_jobs = job_queue.get_jobs_by_name(job_name)
	for job in current_jobs:
		job.schedule_removal()
	
	# especifica o horário
	horario = datetime.time(hour=7, minute=0, tzinfo=ZoneInfo(user_info['tz']))
	
	# agenda
	job_queue.run_daily(
		_forecast_callback,
		time=horario,
		days=(0, 1, 2, 3, 4, 5, 6),
		name=job_name,
		chat_id=chat_id,
		data=user_info # passa o dic como argumento
	)

# city persistence
async def city(update: Update, context):
	"""Saves or print the city name"""
	if len(context.args) < 1:
		user_info = load_user_info()

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

			# Se não achou a cidade
			if 'results' not in resp_data:
				await update.message.reply_text("Desculpe, não consegui encontrar essa cidade.")
				return

			lat = resp_data['results'][0]["latitude"]
			lon = resp_data['results'][0]["longitude"]
			tz = resp_data['results'][0]["timezone"]

			user_info = load_user_info()
			user_info['city'] = city
			user_info['lon'] = lon
			user_info['tz'] = tz
			save_user_info(user_info)

			# atualiza as notificações
			if user_info.get('notify') and user_info.get('chat_id'):
				schedule_forecast(context.job_queue, "forecast", user_info['chat_id'], user_info)
	
			await update.message.reply_text(f"Cidade atualizada para {city}.\nLatitude = {lat}\nlongitude = {lon}")
		except requests.exceptions.RequestException as e:
				logger.error(f"Erro ao buscar latitude e longitude: {e}")
				await update.message.reply_text("Desculpe, não consegui atualizar sua cidade agora. Tente novamente mais tarde.")