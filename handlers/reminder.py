import asyncio

from aiogram.dispatcher import FSMContext  # Импортируем машино состояние

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher

from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from data_base import sql_db
from create_bot import logger
import datetime
from handlers.super_user import AdminOrSuperuserFilter


MINUTE_TO_SECOND: int = 60


class FSMReminder(StatesGroup):
    name_reminder = State()
    text_reminder = State()
    reminder_time = State()


async def reminder(message: types.Message):
    logger.info('Запущена функция reminder (Машино состояние для создания напоминания)')
    await FSMReminder.name_reminder.set()
    await message.reply('Введите название напоминания (Не более 5 слов):')


# Ловим первый ответ от пользователя
async def load_name_reminder(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        name_reminder = ' '.join(message.text.split()[:5])
        data['name_reminder'] = name_reminder[:50]
    await FSMReminder.next()
    await message.reply('Введи текст напоминания')


# Ловим второй ответ от пользователя
async def load_text_reminder(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['text_reminder'] = message.text
    await FSMReminder.next()
    await message.reply('Введи через какое количество минут выводить напоминание')


#Ловим третий ответ от пользователя
async def load_time_second(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        if not message.text.isdigit():
            await message.reply('Вы ввели неправильное значение. Нужно вводить только целое число.')
            return

        data['reminder_interval'] = MINUTE_TO_SECOND*int(message.text)
        data['owner_reminder_id'] = message.from_user.id
        data['reminder_chat_id'] = message.chat.id

    await sql_db.sql_reminder_add_command(state)
    await state.finish()

    reminder_number = sql_db.get_reminder_id(data['reminder_chat_id'])
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


async def read_reminder(message: types.Message):
    logger.info('Запрошен список напоминаний в базу данных через функцию read_reminder')
    global ADMIN_CHAT_ID
    ADMIN_CHAT_ID = message.from_user.id
    if message.from_user.id == ADMIN_CHAT_ID:
        # получаем идентификатор чата
        chat_id = message.chat.id
        chat_name = message.chat.title if message.chat.type != 'private' else 'Личных сообщений'
        # читаем напоминания из базы данных для данного чата
        reminders = await sql_db.sql_reminder_read(chat_id=chat_id)
        if reminders:
            # формируем список напоминаний для данного чата
            reminders_text = '\n\n'.join(reminders)
            await message.reply('Отправлено в ЛС')
            await bot.send_message(chat_id=message.from_user.id, text=f"Это список ваших напоминаний для чата {chat_name}:\n\n{reminders_text}")
        else:
            await bot.send_message(chat_id=message.from_user.id, text=f"У вас нет сохраненных напоминаний для чата {chat_name}")
    else:
        await bot.send_message(chat_id=message.chat.id, text="Данная информация доступна только администратору")



async def start_reminder(reminder_id: int, chat_id: int):
    # записываем время запуска в базу данных
    sql_db.reminder_set_last_view_time(reminder_id, datetime.datetime.now())
    # устанавливаем статус "включено" для напоминания
    sql_db.reminder_set_status(reminder_id, True)
    # устанавливаем флаг "первый запуск"
    first_run = True
    while True:
        # получаем информацию о напоминании из базы данных
        reminder = sql_db.reminder_get(reminder_id)
        if reminder is None:
            # если напоминание удалено из базы данных, выходим из цикла
            break
        text = reminder['text']
        time = int(reminder['time'])
        now = datetime.datetime.now()
        if now.hour >= 23 or (first_run and now.hour < 8):
            # если сейчас позднее 22:00 или это первый запуск и сейчас раньше 8:00,
            # то пропускаем напоминание и выводим уведомление
            if first_run:
                await bot.send_message(chat_id=chat_id, text=f"Время позднее, останавливаю отправку уведомлений")
            next_day = now.date() + datetime.timedelta(days=1)
            next_morning = datetime.datetime.combine(next_day, datetime.time(hour=8))
            time_to_wait = (next_morning - now).seconds
            await asyncio.sleep(time_to_wait)
            await bot.send_message(chat_id=chat_id, text="Доброе утро, уважаемые коллеги СМУ!")
            now = datetime.datetime.now()
            time_to_wait = time - (now - next_morning).seconds
        else:
            # иначе ждем до времени напоминания
            time_to_wait = time
        await asyncio.sleep(time_to_wait)
        # отправляем напоминание
        await bot.send_message(chat_id=chat_id, text=f"(id:{reminder_id})Напоминаю Вам:\n {text}")
        # получаем новый статус из базы данных
        status = sql_db.reminder_get_status(reminder_id)
        if not status:
            # если статус изменился на "выключено", выходим из цикла
            break
        # устанавливаем флаг "первый запуск" в False
        first_run = False
    # устанавливаем статус "выключено" для напоминания
    sql_db.reminder_set_status(reminder_id, False)


async def remind_me(message: types.Message):
    logger.info('Пользователь осуществил запуск напоминания командой /старт в функции remind_me')
    reminder_name = message.text.split(' ')[1]
    chat_id = message.chat.id  # получаем chat_id из сообщения

    # записываем chat_id в базу данных
    sql_db.reminder_set_chat_id(chat_id, int(reminder_name))

    reminders = sql_db.reminder_getbase()

    try:
        reminder_id = int(reminder_name)
        if reminder_id not in reminders:
            await message.reply(f'Напоминание с id {reminder_id} не найдено')
            return
    except ValueError:
        logger.debug('Вызвано исключение ValueError в функции remind_me')
        if reminder_name not in reminders:
            await message.reply(f'Напоминание "{reminder_name}" не найдено')
            return
        reminder_id = reminders[reminder_name]['id']

    await message.reply(f'Ок...')
    asyncio.create_task(start_reminder(reminder_id, chat_id))


async def stop_reminder(message: types.Message):
    logger.info('Пользователь остановил напоминание командой /стоп функцией stop_reminder')
    reminder_id_str = message.text.split(' ')[1]
    reminders = sql_db.reminder_getbase()

    try:
        reminder_id = int(reminder_id_str)
        if reminder_id not in reminders:
            await message.reply(f'Напоминание с id {reminder_id} не найдено')
            return
    except ValueError:
        logger.debug('Вызвано исключение ValueError в функции stop_reminder')
        if reminder_id_str not in reminders:
            await message.reply(f'Напоминание "{reminder_id_str}" не найдено')
            return
        reminder_id = reminders[reminder_id_str]['id']

    sql_db.reminder_set_status(reminder_id, False)
    logger.info('Напоминание успешно остановлено')
    await message.reply(f'Напоминание {reminder_id} успешно остановлено')



async def check_reminders_status():
    logger.info('Запущена функция check_reminders_status для проверки статуса включености напоминаний в базе данных')
    reminders = sql_db.reminder_getbase()
    for reminder_id, reminder in reminders.items():
        if sql_db.reminder_get_status(reminder_id):
            reminder_chat_id = sql_db.reminder_get_chat_id(reminder_id)
            asyncio.create_task(start_reminder(reminder_id, reminder_chat_id))
            logger.debug('функция check_reminders_status для проверки статуса успешно отработала')


async def delete_reminder(message: types.Message):
    logger.info('Пользователем командой /удалить запущена функция delete_reminder для удаления напоминания из БД')
    reminder_id_str = message.text.split(' ')[1]
    reminders = sql_db.reminder_getbase()

    try:
        reminder_id = int(reminder_id_str)
        if reminder_id not in reminders:
            await message.reply(f'Напоминание "{reminder_id_str}" не найдено')
            return
    except ValueError:
        if reminder_id_str not in reminders:
            await message.reply(f'Напоминание "{reminder_id_str}" не найдено')
            return
        reminder_id = reminders[reminder_id_str]['id']
    await message.reply(f'Напоминание {reminder_id_str} удалено из базы данных')
    await sql_db.reminder_delete_command(reminder_id);


dp.filters_factory.bind(AdminOrSuperuserFilter) # добавляет фильтр использования суперюзера
def register_handlers_reminder(dp: Dispatcher):
    dp.register_message_handler(reminder, commands='напомни', state=None, is_admin_or_super=True)
    dp.register_message_handler(load_name_reminder, content_types=['text'], state=FSMReminder.name_reminder)
    dp.register_message_handler(load_text_reminder, content_types=['text'], state=FSMReminder.text_reminder)
    dp.register_message_handler(load_time_second, state=FSMReminder.reminder_time)
    dp.register_message_handler(read_reminder, commands='напоминания', is_admin_or_super=True)
    dp.register_message_handler(delete_reminder, commands=['удалить'], is_admin_or_super=True)
    dp.register_message_handler(stop_reminder, commands=['стоп'], is_admin_or_super=True)
    dp.register_message_handler(remind_me, commands=['старт'], is_admin_or_super=True)



