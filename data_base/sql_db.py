import datetime
import sqlite3 as sq
from typing import Dict, Any

import handlers.super_user
from create_bot import bot, logger



# Создаем базу данных админки
def sql_start():
    global base, cur
    base = sq.connect('SMEL_BASE.db')
    cur = base.cursor()
    if base:
        print('Data Base connected "OK"')
    base.execute('CREATE TABLE IF NOT EXISTS people('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                 'first_name TEXT DEFAULT None,'
                 'last_name TEXT DEFAULT None,'
                 'father_name TEXT DEFAULT None,'
                 'tg_id INTEGER DEFAULT None,'
                 'tg_name TEXT DEFAULT None,'
                 'email TEXT DEFAULT None,'
                 'mega_admin_status BOOLEAN DEFAULT False'
                 ')')

    base.execute('CREATE TABLE IF NOT EXISTS reminders('
                 'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                 'name_reminder TEXT,'
                 'text_reminder TEXT,'
                 'reminder_interval TEXT,'
                 'status_reminder BOOLEAN DEFAULT False,'
                 'created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
                 'owner_reminder_id TEXT,'
                 'reminder_chat_id TEXT,'
                 'reminder_last_view_time TIMESTAMP  DEFAULT None,'  # Последнее время отправки уведомления
                 'reminder_in_day DEFAULT None,'  # День уведомления (Пн,Вт,Ср,Чт,Пт,Cб,Вс)
                 'reminder_day_number DEFAULT None,'  # Число месяца
                 'reminder_month DEFAULT None'  # месяц
                 ')')
    cur.execute('SELECT tg_id FROM people WHERE mega_admin_status = True')
    handlers.super_user.MEGA_ADMINS = [str(row[0]) for row in cur.fetchall()]
    print(f'MEGA_ADMINS in DataBases: {handlers.super_user.MEGA_ADMINS}')
    base.commit()


# Получаем данные от Машиносостояний админки ( переменные img,name,description,price)
async def sql_add_command(state):
    async with state.proxy() as data:
        values = (data['img'], data['name'], data['description'], data['price'])
        cur.execute('INSERT INTO menu VALUES (?, ?, ?, ?)', values)
        base.commit()
async def sql_super_user_command(state):
    async with state.proxy() as data:
        values = (data['tg_id'])
        cur.execute('INSERT INTO people VALUES (?)', values)
        base.commit()


async def sql_add_mega_admin(id_to_add, name_to_add):
    cur.execute('SELECT mega_admin_status FROM people WHERE tg_id = ?', (id_to_add,))
    result = cur.fetchone()
    if result is None:
        cur.execute('INSERT INTO people (tg_id, tg_name, mega_admin_status) VALUES (?, ?, ?)', (id_to_add, name_to_add, True))
        base.commit()
        cur.execute('SELECT tg_id FROM people')
        MEGA_ADMINS = [str(row[0]) for row in cur.fetchall()]
        print("MEGA_ADMINS in DB:", MEGA_ADMINS)
        return True
    elif result[0] == False:
        cur.execute('UPDATE people SET tg_name = ?, mega_admin_status = ? WHERE tg_id = ?', (name_to_add, True, id_to_add))
        base.commit()
        cur.execute('SELECT tg_id FROM people WHERE mega_admin_status == True')
        MEGA_ADMINS = [str(row[0]) for row in cur.fetchall()]
        print("MEGA_ADMINS in DB:", MEGA_ADMINS)
        return True
    else:
        return False


async def sql_del_mega_admin(id_to_del):
    cur.execute('SELECT tg_id, mega_admin_status FROM people WHERE tg_id = ?', (id_to_del,))
    result = cur.fetchone()
    if result is None or not result[1]:
        return False
    else:
        cur.execute('UPDATE people SET mega_admin_status = ? WHERE tg_id = ?', (False, id_to_del))
        base.commit()
        cur.execute('SELECT tg_id FROM people WHERE mega_admin_status == True')
        MEGA_ADMINS = [str(row[0]) for row in cur.fetchall()]
        print("MEGA_ADMINS in DB:", MEGA_ADMINS)
        return True


def sql_list_mega_admin():
    cur.execute('SELECT tg_name, tg_id FROM people WHERE mega_admin_status = True')
    mega_admins = cur.fetchall()
    if mega_admins:
        result = "В базе данных следующие мега админы:\n"
        for admin in mega_admins:
            result += f"Имя {admin[0]}, ТГ ИД: {admin[1]}\n"
        return result
    else:
        return "В базе данных нет мега_админов"





# получаем данные от машинысостояний Reminder
async def sql_reminder_add_command(state):
    async with state.proxy() as data:
        name = data['name_reminder']
        text = data['text_reminder']
        time = data['reminder_interval']
        owner_reminder_id = data['owner_reminder_id']
        reminder_chat_id = data['reminder_chat_id']
        created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = False
        cur.execute(
            "INSERT INTO reminders ("
            "name_reminder,"
            " text_reminder,"
            " reminder_interval,"
            " status_reminder,"
            " created_at,"
            " owner_reminder_id,"
            " reminder_chat_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, text, time, status, created_at, owner_reminder_id, reminder_chat_id))
        base.commit()


# читаем базу данных и посылаем сообщение в чат
async def sql_reminder_read(chat_id):
    reminders = cur.execute('SELECT * FROM reminders WHERE reminder_chat_id = ?', (chat_id,)).fetchall()
    if len(reminders) == 0:
        return ['-== Напоминаний не создано ==-']
    else:
        reminder_list = []
        for reminder in reminders:
            (id,
             name_reminder,
             text_reminder,
             reminder_interval,
             status_reminder,
             created_at,
             owner_reminder_id,
             reminder_chat_id,
             reminder_last_view_time,
             reminder_in_day,
             reminder_day_number,
             reminder_month) = reminder
            if status_reminder:
                active_status = 'Включено'
            else:
                active_status = 'Выключено'
            reminder_time_minute = int(reminder_interval) / 60
            reminder_info = f'''
Напоминание № {id},
Статус напоминания: "{active_status}",
Имя напоминания: "{name_reminder}",
Интервал повторения: "{reminder_time_minute}" мин.,'''
            reminder_list.append(reminder_info)

        return reminder_list



# С помощью этой функции получаем значения в виде словаря из базы там где ее запросят в reminder
def reminder_getbase():
    reminders = cur.execute('SELECT * FROM reminders').fetchall()
    if len(reminders) == 0:
        return {}
    else:
        result = {}
        for reminder in reminders:
            (id,
             name_reminder,
             text_reminder,
             reminder_interval,
             status_reminder,
             created_at,
             owner_reminder_id,
             reminder_chat_id,
             reminder_last_view_time,
             reminder_in_day,
             reminder_day_number,
             reminder_month) = reminder
            result[id] = {'reminder_id': id,
                          'name': name_reminder,
                          'text': text_reminder,
                          'time': reminder_interval,
                          'status': status_reminder,
                          'created_at': created_at,
                          'owner_reminder_id': owner_reminder_id,
                          'reminder_chat_id': reminder_chat_id,
                          'reminder_last_view_time': reminder_last_view_time,
                          'reminder_in_day': reminder_in_day,
                          'reminder_day_number': reminder_day_number,
                          'reminder_month': reminder_month}
        return result


def reminder_set_status(reminder_id: int, status: bool):
    cur.execute("UPDATE reminders SET status_reminder = ? WHERE id = ?", (status, reminder_id))
    base.commit()


def reminder_get_status(reminder_id: int) -> bool:
    cur.execute("SELECT status_reminder FROM reminders WHERE id = ?", (reminder_id,))
    result = cur.fetchone()
    return bool(result[0]) if result else False


def reminder_get_chat_id(reminder_id: int) -> str:
    cur.execute("SELECT reminder_chat_id FROM reminders WHERE id = ?", (reminder_id,))
    result = cur.fetchone()
    return result[0] if result else "default_chat_id"


async def reminder_delete_command(reminder_id: int):
    # Проверяем наличие напоминания с заданным id в базе данных
    cur.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,))
    result = cur.fetchone()
    if result is None:
        print('АХАХАХАХХА')
        return

    # Удаляем напоминание с заданным id из базы данных
    cur.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    base.commit()



def get_reminder_id(chat_id: str) -> int:
    cur.execute("SELECT id FROM reminders WHERE reminder_chat_id = ? ORDER BY id DESC LIMIT 1", (chat_id,))
    result = cur.fetchone()
    return result[0] if result else None





def reminder_get(reminder_id):
    reminder = cur.execute('SELECT * FROM reminders WHERE id=?', (reminder_id,)).fetchone()
    if reminder is None:
        return None
    else:
        (id,
         name_reminder,
         text_reminder,
         reminder_interval,
         status_reminder,
         created_at,
         owner_reminder_id,
         reminder_chat_id,
         reminder_last_view_time,
         reminder_in_day,
         reminder_day_number,
         reminder_month) = reminder
        return {'reminder_id': id,
                'name': name_reminder,
                'text': text_reminder,
                'time': reminder_interval,
                'status': status_reminder,
                'created_at': created_at,
                'owner_reminder_id': owner_reminder_id,
                'reminder_chat_id': reminder_chat_id,
                'reminder_last_view_time': reminder_last_view_time,
                'reminder_in_day': reminder_in_day,
                'reminder_day_number': reminder_day_number,
                'reminder_month': reminder_month}

def reminder_set_last_view_time(reminder_id: int, created_at: datetime.datetime):
    cur.execute("UPDATE reminders SET reminder_last_view_time= ? WHERE id = ?", (created_at, reminder_id))
    base.commit()

def reminder_set_chat_id(chat_id: int, id: int):
    cur.execute('UPDATE reminders SET reminder_chat_id = ? WHERE id = ?', (chat_id, id))
    base.commit()
def reminder_get_by_chat_id(chat_id):
    """Возвращает список напоминаний, созданных в указанном чате."""
    with sq.connect('SMEL_BASE.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM reminders WHERE reminder_chat_id=? AND status_reminder=0", (chat_id,))
        rows = cur.fetchall()

        # преобразовываем список кортежей в список словарей
        reminders = []
        for row in rows:
            reminder = {
                'id': row[0],
                'name': row[1],
                'text': row[2],
                'interval': row[3],
                'status': row[4],
                'created_at': row[5],
                'owner_id': row[6],
                'chat_id': row[7],
                'last_view_time': row[8],
                'day': row[9],
                'day_number': row[10],
                'month': row[11]
            }
            reminders.append(reminder)

        return reminders


def reminder_list_by_chat_id(chat_id):
    """Возвращает список напоминаний для указанного чата."""
    reminders = reminder_get_by_chat_id(chat_id)
    if not reminders:
        return f'Д'



