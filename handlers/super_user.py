import asyncio

from aiogram.dispatcher import FSMContext  # Импортируем машино состояние

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from data_base import sql_db
from create_bot import logger
import datetime
from create_bot import SUPER_USERS
from aiogram.dispatcher.filters import BoundFilter

class AdminOrSuperuserFilter(BoundFilter):
    """ Класс позволяет управлять ботом в любых чатах суперпользователю и назначеным им людям"""
    key = 'is_admin_or_super'

    def __init__(self, is_admin_or_super):
        self.is_admin_or_super = is_admin_or_super

    async def check(self, message: types.Message):
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.is_chat_admin():
            return True
        elif str(message.from_user.id) in SUPER_USERS:
            return True
        else:
            return False

def register_handlers_super_user(dp: Dispatcher):
    dp.filters_factory.bind(AdminOrSuperuserFilter)