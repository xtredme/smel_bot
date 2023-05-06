from aiogram.utils import executor
from create_bot import dp
from handlers import client, admin, other,reminder
from data_base import sql_db
from handlers.reminder import check_reminders_status
from create_bot import logger


async def on_startup(_):
    logger.info('Бот успешно запущен')
    sql_db.sql_start()
    logger.debug('База данных админки стартовала')
    sql_db.sql_start_reminder()
    logger.debug('База Reminder успешно стартовала')
    await check_reminders_status()


client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
reminder.register_handlers_reminder(dp)
other.register_handlers_other(dp) # Должен быть последним т.к есть неименованый handler



if __name__ == '__main__':
    # Запускаем цикл обработки входящих сообщений
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    logger.info('if__name__=main и start polling успешно запущены')