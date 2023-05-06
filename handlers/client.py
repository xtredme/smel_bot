from keyboards import kb_client
from aiogram.dispatcher.filters import Text
from data_base import sql_db, info_mes
from aiogram import Dispatcher, types
from create_bot import logger, dp
from handlers.super_user import AdminOrSuperuserFilter


async def command_start(message: types.Message):
    logger.info('Запущена приветственное сообщение командой /start или /help')
    hi_message = info_mes.hello_message
    try:
        await message.answer( hi_message) #reply_markup=kb_client
        await message.delete()
    except:
        await message.reply('Общение с ботом через ЛС, напишите ему:')


async def command_smy_people(message: types.Message):
    logger.info('Запущена команда /состав_сму со списком участнмков')
    chat_member = await message.chat.get_member(message.from_user.id)
    if chat_member.status == types.ChatMemberStatus.OWNER: #проверяем администратор ли пользователь
        sostav_smy = info_mes.info_people
        people_info = ""

        # Итерируемся по словарю и добавляем информацию о каждом человеке к строке
        for id, person in sostav_smy.items():
            for name, position in person.items():
                people_info += f"{id}. {name} - {position}\n"

        await message.answer(people_info)
    else:
        await message.reply("Ты не имеешь доступа к этой информации")




async def photo_last_object(message: types.Message):
    logger.info('Запущена команда /фото_последних_объектов')
    await message.reply('Вот фото последних объектов: Будет дополнено')

async def smy_menu(message: types.Message):
    logger.info('Запущена команда /Меню;;;')
    await sql_db.sql_read(message)




async def smy_best(message: types.Message): #ловим слово (которое указываем в регистрации ниже)и делаем действие
    await message.reply('Вы хотели сказать: "СМУ лучше всех"?)')

dp.filters_factory.bind(AdminOrSuperuserFilter) # добавляет фильтр использования суперюзера
def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(command_smy_people, commands=['состав_сму'])
    dp.register_message_handler(photo_last_object, commands=['Фото_последних_объектоввфвф'])
    dp.register_message_handler(smy_menu, commands=['Меню;;;'])
    dp.register_message_handler(smy_best, Text(equals='СМУ', ignore_case=True), state="*")



