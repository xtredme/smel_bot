import string, json

from aiogram import Dispatcher, types
#await message.answer(message.text)  # просто отвечает в чат
#await message.reply(message.text) # отвечает с упоминанием
#await bot.send_message(message.from_user.id, message.text) # напишет в личку сообщение, которое отправлено в группе


#@dp.message_handler()
async def echo_send(message: types.Message):
    if {i.lower().translate(str.maketrans('',
                                          '',
                                          string.punctuation)) for i in message.text.split(' ')}\
            .intersection(set(json.load(open('bad_words.json')))) != set():
        await message.reply('Маты запрещены')
        await message.delete()

def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(echo_send)
