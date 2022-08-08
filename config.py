
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import os
from aiogram.dispatcher import Dispatcher
from aiogram import Bot, types

TOKEN = os.getenv('BOT_TOKEN')
print(TOKEN)
service_bot = Bot(token='SERVICE_BOT_TOKEN')
print(service_bot)
client_bot = Bot(token='BOT_TOKEN')
dp = Dispatcher(service_bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
WEBAPP_PORT = os.getenv('PORT', default=5000)


if not TOKEN:
    print('You have forgot to set BOT_TOKEN')
    quit()

