import string, json
from create_bot import dp
from aiogram import Dispatcher, types
from handlers.super_user import AdminOrSuperuserFilter


async def echo_send(message: types.Message):
    if {i.lower().translate(str.maketrans('',
                                          '',
                                          string.punctuation)) for i in message.text.split(' ')}\
            .intersection(set(json.load(open('bad_words.json')))) != set():
        await message.reply('Маты запрещены !')
        await message.delete()


dp.filters_factory.bind(AdminOrSuperuserFilter) # добавляет фильтр использования суперюзера
def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(echo_send)
