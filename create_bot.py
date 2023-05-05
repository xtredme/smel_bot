from aiogram import Bot, Dispatcher
import os
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage #Оперативная память либо Монго
from dotenv import load_dotenv

storage = MemoryStorage()

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_MYCHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CHAT_ID = os.getenv('CHAT_ID') #ID чата
CHANEL_ID = os.getenv('CHANEL_ID')
RETRY_TIME = 600

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN) # Создаем бота
dp = Dispatcher(bot, storage = storage)