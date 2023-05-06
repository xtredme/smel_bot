
from aiogram import types, Dispatcher
from create_bot import dp
from create_bot import bot, SUPER_USERS
from aiogram.dispatcher.filters import BoundFilter
import sqlite3 as sq

MEGA_ADMINS = []
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
        elif str(message.from_user.id) in MEGA_ADMINS:
            return True
        else:
            return False


def sql_super_user_start():
    global base, cur, MEGA_ADMINS
    base = sq.connect('mega_admin.db')
    cur = base.cursor()
    if base:
        print('MEGA_ADMIN Data Base connected "OK"')
    base.execute('CREATE TABLE IF NOT EXISTS menu(mega_admin_id TEXT PRIMARY KEY)')
    base.commit()

    # Получаем список мега-админов из базы данных
    cur.execute('SELECT mega_admin_id FROM menu')
    MEGA_ADMINS = [str(row[0]) for row in cur.fetchall()]
    print("MEGA_ADMINS:", MEGA_ADMINS) # for debugging purposes


# Получаем данные от Машиносостояний админки ( переменные img,name,description,price)
async def sql_super_user_command(state):
    async with state.proxy() as data:
        values = (data['mega_admin_id'])
        cur.execute('INSERT INTO menu VALUES (?)', values)
        base.commit()


async def update_mega_admins_list():
    global MEGA_ADMINS
    cur.execute('SELECT mega_admin_id FROM menu')
    MEGA_ADMINS = [str(row[0]) for row in cur.fetchall()]
    print("MEGA_ADMINS:", MEGA_ADMINS)

async def add_mega_admin_handler(message: types.Message):
    if str(message.from_user.id) in SUPER_USERS:
        reply_user_id = message.reply_to_message.from_user.id
        cur.execute('INSERT OR IGNORE INTO menu (mega_admin_id) VALUES (?)', (str(reply_user_id),))
        if cur.rowcount == 0:
            await message.answer("Этот пользователь уже есть в списке мега-админов")
        else:
            base.commit()
            await update_mega_admins_list()
            await message.answer(f"Пользователь добавлен в список мега-админов.\n"
                                 f"Теперь пользователю доступно управление ботом в чатах\n"
                                 f"где он не является администратором")
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

async def delete_mega_admin_handler(message: types.Message):
    if str(message.from_user.id) in SUPER_USERS:
        reply_user_id = message.reply_to_message.from_user.id
        cur.execute('DELETE FROM menu WHERE mega_admin_id = ?', (str(reply_user_id),))
        if cur.rowcount == 0:
            await message.answer("Этого пользователя нет в списке мега-админов")
        else:
            base.commit()
            await update_mega_admins_list()
            await message.answer(f"Пользователь удален из списка мега-админов\n")
    else:
        await message.answer("У вас нет прав на выполнение этой команды.")

dp.filters_factory.bind(AdminOrSuperuserFilter)
def register_handlers_super_user(dp: Dispatcher):
    dp.register_message_handler(add_mega_admin_handler, commands=['добавить_мега_админ'], is_reply=True)
    dp.register_message_handler(delete_mega_admin_handler, commands=['удалить_мега_админ'], is_reply=True)


