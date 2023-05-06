from aiogram import Bot, Dispatcher
import os
import logging
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

storage = MemoryStorage()

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_MYCHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CHAT_ID = os.getenv('CHAT_ID')
CHANEL_ID = os.getenv('CHANEL_ID')
RETRY_TIME = 600
SUPER_USERS = os.getenv('SUPER_USERS')


# Создаем объект логгера и указываем его имя
logger = logging.getLogger('smel_bot_logger')
logger.setLevel(logging.DEBUG)

# Создаем объект обработчика для записи логов в файл
file_handler = logging.FileHandler('smel_bot.log')
file_handler.setLevel(logging.INFO)

# Устанавливаем формат сообщений лога
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(file_handler)


bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=storage)




