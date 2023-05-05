import datetime
import sqlite3 as sq
from create_bot import dp, bot, CHAT_ID

#Создаем базу данных админки
def sql_start():
    global base, cur
    base = sq.connect('smy_xd.db')
    cur = base.cursor()
    if base:
        print('Data Base connected "OK"')
    base.execute('CREATE TABLE IF NOT EXISTS menu(img TEXT, name TEXT PRIMARY KEY, description TEXT, price TEXT)')
    base.commit()

#Получаем данные от Машиносостояний админки ( переменные img,name,description,price)
async def sql_add_command(state):
    async with state.proxy() as data:
        values = (data['img'], data['name'], data['description'], data['price'])
        cur.execute('INSERT INTO menu VALUES (?, ?, ?, ?)', values)
        base.commit()
#читаем базу данных админки и отправляем сообщение
async def sql_read(message):
    for ret in cur.execute('SELECT * FROM menu').fetchall():
        await bot.send_photo(message.from_user.id, ret[0], f'{ret[2]}\nЦена {ret[-1]}')

### Создаем базу данных Reminder
def sql_start_reminder():
    global base_reminder, cur_reminder
    base_reminder = sq.connect('base_reminder.db')
    cur_reminder = base_reminder.cursor()
    if base_reminder:
        print('База данных напоминаний загружена')
    base_reminder.execute('CREATE TABLE IF NOT EXISTS menu('
                          'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                          ' name_reminder TEXT,'
                          ' text_reminder TEXT,'
                          ' reminder_time TEXT,'
                          ' status_reminder BOOLEAN DEFAULT False,'
                          ' created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
                          'owner_reminder_id TEXT,'
                          'reminder_chat_id TEXT'
                          ')')

    base_reminder.commit()


#получаем данные от машинысостояний Reminder
async def sql_reminder_add_command(state):
    async with state.proxy() as data:
        name = data['name_reminder']
        text = data['text_reminder']
        time = data['reminder_time']
        owner_reminder_id = data['owner_reminder_id']
        reminder_chat_id = data['reminder_chat_id']
        created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = False
        cur_reminder.execute(
            "INSERT INTO menu (name_reminder, text_reminder, reminder_time, status_reminder, created_at, owner_reminder_id, reminder_chat_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, text, time, status, created_at, owner_reminder_id, reminder_chat_id))
        base_reminder.commit()

#читаем базу данных и посылаем сообщение в чат
async def sql_reminder_read(message):
    reminders = cur_reminder.execute('SELECT * FROM menu').fetchall()
    if len(reminders) == 0:
        await bot.send_message(chat_id=message.chat.id, text='Нет сохраненных напоминаний.')
    else:
        await bot.send_message(chat_id=message.chat.id, text=f'Вот список всех ваших напоминаний:')
        for reminder in reminders:
            id, name_reminder, text_reminder, reminder_time, status_reminder, created_at, owner_reminder_id, reminder_chat_id= reminder
            if status_reminder == True:
                active_status = 'Включено'
            else:
                active_status = 'Выключено'
            await bot.send_message(chat_id=message.chat.id, text=f'''
Напоминание № {id},
Статус напоминания: "{active_status}",
Имя напоминания: "{name_reminder}",
Текст напоминания: "{text_reminder}",
Время повторения: "{reminder_time}" секунд,
Время создания напоминания:"{created_at}",
Создатель напоминаний: {owner_reminder_id},
Чат напоминания: {reminder_chat_id}
''')
#С помощью этой функции получаем значения в виде словаря из базы там где ее запросят в reminder
def reminder_getbase():
    reminders = cur_reminder.execute('SELECT * FROM menu').fetchall()
    if len(reminders) == 0:
        return {}
    else:
        result = {}
        for reminder in reminders:
            id, name_reminder, text_reminder, reminder_time, status_reminder, created_at, owner_reminder_id, reminder_chat_id= reminder
            result[id] = {'name': name_reminder, 'text': text_reminder, 'time': reminder_time, 'status': status_reminder, 'created_at': created_at}
        return result

def reminder_set_status(reminder_id: int, status: bool):
    cur_reminder.execute("UPDATE menu SET status_reminder = ? WHERE id = ?", (status, reminder_id))
    base_reminder.commit()

def reminder_get_status(reminder_id: int) -> bool:
    cur_reminder.execute("SELECT status_reminder FROM menu WHERE id = ?", (reminder_id,))
    result = cur_reminder.fetchone()
    return bool(result[0]) if result else False

def reminder_get_chat_id(reminder_id: int) -> str:
    cur_reminder.execute("SELECT reminder_chat_id FROM menu WHERE id = ?", (reminder_id,))
    result = cur_reminder.fetchone()
    return result[0] if result else None

async def reminder_delete_command(reminder_id: int):
    # Проверяем наличие напоминания с заданным id в базе данных
    cur_reminder.execute("SELECT * FROM menu WHERE id = ?", (reminder_id,))
    result = cur_reminder.fetchone()
    if result is None:
        await bot.send_message(chat_id=reminder_get_chat_id(reminder_id), text=f'Напоминание не найдено.')
        return

    # Удаляем напоминание с заданным id из базы данных
    cur_reminder.execute("DELETE FROM menu WHERE id = ?", (reminder_id,))
    base_reminder.commit()

    # Обновляем id всех записей с id > reminder_id
    cur_reminder.execute("UPDATE menu SET id = id - 1 WHERE id > ?", (reminder_id,))
    base_reminder.commit()

    await bot.send_message(chat_id=reminder_get_chat_id(reminder_id), text=f'Напоминание № {reminder_id} удалено.')




def get_reminder_id(chat_id: str) -> int:
    cur_reminder.execute("SELECT id FROM menu WHERE reminder_chat_id = ?", (chat_id,))
    result = cur_reminder.fetchone()
    return result[0] if result else None




