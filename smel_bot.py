from aiogram.utils import executor
from create_bot import dp
from handlers import client, admin, other,reminder, super_user
from data_base import sql_db
from handlers.reminder import check_reminders_status
from create_bot import logger
from handlers.super_user import MEGA_ADMINS


async def on_startup(_):
    logger.info('Бот успешно запущен')
    sql_db.sql_start()
    logger.debug('База данных Admin успешно стартовала')
    sql_db.sql_start_reminder()
    logger.debug('База данных Reminder успешно стартовала')
    super_user.sql_super_user_start()
    logger.debug('База данных Mega Admin успешно стартовала')
    await check_reminders_status()


client.register_handlers_client(dp)
admin.register_handlers_admin(dp)
reminder.register_handlers_reminder(dp)
super_user.register_handlers_super_user(dp)
other.register_handlers_other(dp)  # Должен быть последним т.к есть неименованный handler



if __name__ == '__main__':
    # Запускаем цикл обработки входящих сообщений
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    logger.info('if__name__=main и start polling успешно запущены')