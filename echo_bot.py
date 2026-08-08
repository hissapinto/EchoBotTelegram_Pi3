from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import logging
import os

# Importar os arquivo
from alarms import alarm_min, alarm_days
from forecast import forecast, reschedule_forecast, city
from basic_commands import start, echo, roll, get_time, help, get_fact

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

	# Reschedule forecast notifications
	reschedule_forecast(app)

	# Run the bot until user presses Ctrl-C
	app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=="__main__":
	main()
