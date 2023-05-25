
from aiogram import types, Dispatcher
from create_bot import dp
from create_bot import bot, SUPER_USERS
from aiogram.dispatcher.filters import BoundFilter
from data_base import sql_db
MEGA_ADMINS = [] #TODO: надо передать сюда значения из базы данных


class AdminOrSuperuserFilter(BoundFilter):
    """ Класс позволяет управлять ботом в любых чатах суперпользователю и назначеным им людям"""
    key = 'is_admin_or_super'

    def __init__(self, is_admin_or_super):
        self.is_admin_or_super = is_admin_or_super

    async def check(self, message: types.Message):
        if str(message.from_user.id) in SUPER_USERS:
            return True
        elif str(message.from_user.id) in MEGA_ADMINS:
            return True
        else:
            return False


async def add_mega_admin(message: types.Message):
    if str(message.from_user.id) in SUPER_USERS:
        reply_user_id = message.reply_to_message.from_user.id
        reply_user_name = message.reply_to_message.from_user.username # Получение имени пользователя
        if await sql_db.sql_add_mega_admin(reply_user_id, reply_user_name):
            MEGA_ADMINS.append(str(reply_user_id))
            await message.answer(f"Пользователь {reply_user_name} ({reply_user_id}) добавлен в список мега-админов.\n"
                                 f"Теперь пользователю доступно управление ботом в чатах\n"
                                 f"где он не является администратором")
        else:
            await message.answer(f"Пользователь {reply_user_name} ({reply_user_id}) уже есть в списке мега-админов")
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")



async def del_mega_admin(message:types.Message):
    if str(message.from_user.id) in SUPER_USERS:
        reply_user_id = message.reply_to_message.from_user.id
        if await sql_db.sql_del_mega_admin(reply_user_id):
            MEGA_ADMINS.remove(str(reply_user_id))
            await message.answer(f"Пользователь удален из списка мега-админов\n")
        else:
            await message.answer("Этого пользователя нет в списке мега-админов")
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")


async def mega_admin_list(message:types.Message):
    if str(message.from_user.id) in SUPER_USERS:
        await message.answer(sql_db.sql_list_mega_admin())
        print(f'Мега админы в переменной MEGA_ADMINS: {MEGA_ADMINS}')
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")


dp.filters_factory.bind(AdminOrSuperuserFilter)


def register_handlers_super_user(dp: Dispatcher):
    dp.register_message_handler(del_mega_admin, commands=['удалить_мега_админ'], is_reply=True,  is_admin_or_super=True)
    dp.register_message_handler(mega_admin_list, commands=['список_мега_админ'],  is_admin_or_super=True)
    dp.register_message_handler(add_mega_admin, commands=['мега_админ'],  is_admin_or_super=True)




