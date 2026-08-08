from telegram import Update
import datetime

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
		await update.message.reply_text("Uso: /alarm_min <minutos> <o que você quer lembrar> (ex: /alarm_min 10 Saia de casa)")

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