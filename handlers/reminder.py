import asyncio

from aiogram.dispatcher import FSMContext #Импортируем машиносостояние

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from data_base import sql_db

#Напоминальщик
#создаем глобальную переменную

ID = None

#Создаем и описываем нужное машиносостояние
class FSMReminder(StatesGroup):
    name_reminder = State()
    text_reminder = State()
    reminder_time = State()

"""Проверка админ ли человек"""
#получаем ID текущего модератора
#@dp.message_handler(commands=['moderator'], is_chat_admin = True)


#Начало диалога и машиносостояния reminder
async def reminder(message: types.Message):
    global ID
    ID = message.from_user.id
    if message.from_user.id == ID:

        await FSMReminder.name_reminder.set()
        await message.reply('Введите название напоминания:')
    else:
        await message.reply('Только администраторы могут создавать напоминания!')

#Ловим первый ответ от пользователя
async def load_name_reminder(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['name_reminder'] = message.text
        await FSMReminder.next()
        await message.reply('Введи текст напоминания')
#Ловим второй ответ от пользователя
async def load_text_reminder(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['text_reminder'] = message.text
        await FSMReminder.next()
        await message.reply('Введи через какое количество секунд выводить напоминание')

#Ловим третий ответ от пользователя
async def load_time_second(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            if not message.text.isdigit():
                await message.reply('Вы ввели неправильное значение. Нужно вводить только целое число.')
                return

            data['reminder_time'] = int(message.text)
            data['owner_reminder_id'] = message.from_user.id
            data['reminder_chat_id'] = message.chat.id

        await sql_db.sql_reminder_add_command(state)
        await state.finish()

        reminder_number = sql_db.get_reminder_id(message.chat.id)
        await message.reply(
            f"Напоминанию присвоен №:<b> {reminder_number}.</b>\n"
            f"Для запуска введите команду: <b><i>/старт {reminder_number}</i></b>\n"
            f"Для остановки введите: <b><i>/стоп {reminder_number}</i></b>\n",
            parse_mode="HTML"
        )


#Выход из состояний
@dp.message_handler(state="*", commands='отмена')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cansel_reminder(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Создание напоминания отменено')

@dp.message_handler(commands=['напоминания'])
async def read_reminder(message: types.Message):
    await sql_db.sql_reminder_read(message)
    print(sql_db.reminder_getbase())

async def start_reminder(reminder_id: int, chat_id: int):
    sql_db.reminder_set_status(reminder_id, True)
    status = True
    while status:
        reminders = sql_db.reminder_getbase()
        if reminder_id not in reminders:
            return
        text = reminders[reminder_id]['text']
        time = int(reminders[reminder_id]['time'])
        await asyncio.sleep(time)
        await bot.send_message(chat_id=chat_id, text=f"Напоминание '{reminder_id}': {text}")
        status = sql_db.reminder_get_status(reminder_id)
    sql_db.reminder_set_status(reminder_id, False)




@dp.message_handler(commands=['старт'])
async def remind_me(message: types.Message):
    reminder_name = message.text.split(' ')[1]
    reminders = sql_db.reminder_getbase()

    try:
        reminder_id = int(reminder_name)
        if reminder_id not in reminders:
            await message.reply(f'Напоминание с id {reminder_id} не найдено')
            return
    except ValueError:
        if reminder_name not in reminders:
            await message.reply(f'Напоминание "{reminder_name}" не найдено')
            return
        reminder_id = reminders[reminder_name]['id']

    reminder = reminders[reminder_id]
    await message.reply(f'Напоминаю "{reminder["text"]}" каждые {reminder["time"]} секунд')
    reminder_chat_id = sql_db.reminder_get_chat_id(reminder_id)
    print(f'Чат ID: {reminder_chat_id}')
    asyncio.create_task(start_reminder(reminder_id, message.chat.id)) #TODO

@dp.message_handler(commands=['стоп'])
async def stop_reminder(message: types.Message):
    reminder_id_str = message.text.split(' ')[1]
    reminders = sql_db.reminder_getbase()

    try:
        reminder_id = int(reminder_id_str)
        if reminder_id not in reminders:
            await message.reply(f'Напоминание с id {reminder_id} не найдено')
            return
    except ValueError:
        if reminder_id_str not in reminders:
            await message.reply(f'Напоминание "{reminder_id_str}" не найдено')
            return
        reminder_id = reminders[reminder_id_str]['id']

    sql_db.reminder_set_status(reminder_id, False)
    await message.reply(f'Напоминание с id {reminder_id} остановлено')



async def check_reminders_status():
    print('Проверка статуса напоминаний запущена')
    reminders = sql_db.reminder_getbase()
    for reminder_id, reminder in reminders.items():
        if sql_db.reminder_get_status(reminder_id):
            reminder_chat_id = sql_db.reminder_get_chat_id(reminder_id)
            asyncio.create_task(start_reminder(reminder_id, reminder_chat_id))

@dp.message_handler(commands=['удалить'])
async def delete_reminder(message: types.Message):
    reminder_id_str = message.text.split(' ')[1]
    reminders = sql_db.reminder_getbase()

    try:
        reminder_id = int(reminder_id_str)
        if reminder_id not in reminders:
            await message.reply(f'Напоминание с id {reminder_id} не найдено')
            return
    except ValueError:
        if reminder_id_str not in reminders:
            await message.reply(f'Напоминание "{reminder_id_str}" не найдено')
            return
        reminder_id = reminders[reminder_id_str]['id']
    await message.reply(f'Напоминание удалено из базы данных')
    await sql_db.reminder_delete_command(reminder_id)





def register_handlers_reminder(dp: Dispatcher):
    dp.register_message_handler(reminder, commands='напомни', state=None, is_chat_admin=True)
    dp.register_message_handler(load_name_reminder, content_types=['text'], state=FSMReminder.name_reminder)
    dp.register_message_handler(load_text_reminder, content_types=['text'], state=FSMReminder.text_reminder)
    dp.register_message_handler(load_time_second, state=FSMReminder.reminder_time)



