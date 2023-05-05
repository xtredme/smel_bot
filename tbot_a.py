from aiogram.utils import executor
from create_bot import dp
from handlers import client, admin, other,reminder
from data_base import sql_db
from handlers.reminder import check_reminders_status


async def on_startup(_):
    print('Бот вышел в онлайн')
    sql_db.sql_start()# стартуем базу данных админки
    sql_db.sql_start_reminder()# стартуем базу данных reminder
    await check_reminders_status()


    #await message.answer(message.text)  # просто отвечает в чат
    #await message.reply(message.text) # отвечает с упоминанием
    #await bot.send_message(message.from_user.id, message.text) # напишет в личку сообщение, которое отправлено в группе

client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
reminder.register_handlers_reminder(dp)
other.register_handlers_other(dp) # Должен быть последним т.к есть неименованый handler



if __name__ == '__main__':
    # Запускаем цикл обработки входящих сообщений
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)