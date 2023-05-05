import aiogram

from keyboards import kb_client
from aiogram.dispatcher.filters import Text
from data_base import sql_db, smy
from create_bot import CHAT_ID, bot, dp
from aiogram import Bot, Dispatcher, types
import asyncio

#await message.answer(message.text)  # просто отвечает в чат
#await message.reply(message.text) # отвечает с упоминанием
#await bot.send_message(message.from_user.id, message.text) # напишет в личку сообщение, которое отправлено в группе

#@dp.message_handler(commands=['start', 'help'])

async def command_start(message: types.Message):
    try:
        await message.answer( 'Приветствую, это Бот!', reply_markup=kb_client) # Пишем сообщение в личку пользователю
        await message.delete()
    except:
        await message.reply('Общение с ботом через ЛС, напишите ему: \nhttps://t.me/taurus_dev_bot')
#@dp.message_handler(commands=['Женя'])
async def command_smy_people(message: types.Message):
    chat_member = await message.chat.get_member(message.from_user.id)
    if chat_member.status == types.ChatMemberStatus.OWNER: #проверяем администратор ли пользователь
        sostav_smy = smy.smy_people
        people_info = ""

        # Итерируемся по словарю и добавляем информацию о каждом человеке к строке
        for id, person in sostav_smy.items():
            for name, position in person.items():
                people_info += f"{id}. {name} - {position}\n"

        await message.answer(people_info)
    else:
        await message.reply("Ты не имеешь доступа к этой информации")




async def photo_last_object(message: types.Message):
    await message.reply('Вот фото последних объектов: ...')

async def smy_menu(message: types.Message):
    await sql_db.sql_read(message)



#@dp.message_handler(lambda message: 'бобер' in message.text)
async def pyton(message: types.Message): #ловим слово (которое указываем в регистрации ниже)и делаем действие
    await message.reply('Python - это язык програмирования')





# Пишем сообщение в личку пользователю

def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(command_smy_people, commands=['Состав_СМУ'])
    dp.register_message_handler(photo_last_object, commands=['Фото_последних_объектов'])
    dp.register_message_handler(smy_menu, commands=['Меню'])
    dp.register_message_handler(pyton, Text(equals='питон', ignore_case=True), state="*")



