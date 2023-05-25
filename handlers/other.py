import string, json
from create_bot import dp, bot
from aiogram import Dispatcher, types
from handlers.super_user import AdminOrSuperuserFilter
from txt_to_json import txt_to_json_with_codding
import datetime
from data_base import sql_db


import json



async def echo_send(message: types.Message):
    if {i.lower().translate(str.maketrans('',
                                          '',
                                          string.punctuation)) for i in message.text.split(' ')}\
            .intersection(set(json.load(open('bad_words.json')))) != set():
        await message.reply('Маты запрещены !')
        await message.delete()

def add_bad_word_to_file(word):
    with open('bad_words.txt', 'a') as f:
        f.write(word + '\n')



@dp.message_handler(commands=['мат'])
async def add_bad_word_command_handler(message: types.Message):
    args = message.get_args().split()
    if len(args) == 0:
        await message.reply("Пожалуйста, укажите слово, которое необходимо добавить в список плохих слов.")
        return
    bad_word = args[0]
    add_bad_word_to_file(bad_word)
    txt_to_json_with_codding('bad_words')

    await message.answer(f"Добавлено в список плохих слов.")
    await message.delete()





# создаем хэндлер для команды /извинись
@dp.message_handler(commands=['извинись'])
async def apologize(message: types.Message):
    # получаем данные из сообщения и передаем их в функцию add_to_banlist
    banned_id = message.reply_to_message.from_user.id
    ban_status = True
    need_sorry = True
    created_at = datetime.datetime.now()
    await message.reply(text=f"{banned_id}, {ban_status}, {need_sorry}, {created_at}")
    await sql_db.add_to_banlist(banned_id, ban_status, need_sorry, created_at)
    # отправляем сообщение пользователю, что его сообщения заблокированы
    await message.reply(f"@{message.reply_to_message.from_user.username}, ваши сообщения заблокированы до тех пор, пока вы не извинитесь. Напишите '/извините меня', чтобы разблокировать свои сообщения.")

@dp.message_handler(commands=['удалить_бан'])
async def remove_banlist_entries(message: types.Message):
    # получаем id пользователя, которого нужно разблокировать
    banned_id = message.reply_to_message.from_user.id
    # удаляем все записи из бан-листа для данного пользователя
    await sql_db.remove_from_banlist(banned_id)
    # отправляем сообщение об успешном удалении записей из бан-листа
    await message.reply(f"Все записи из бан-листа для пользователя с ID {banned_id} успешно удалены.")


dp.filters_factory.bind(AdminOrSuperuserFilter) # добавляет фильтр использования суперюзера
def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(add_bad_word_command_handler, commands=['мат'], is_admin_or_super=True)
    dp.register_message_handler(echo_send)
