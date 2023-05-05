from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('/Состав_СМУ')
b2 = KeyboardButton('/Фото_последних_объектов')
b3 = KeyboardButton('/Меню')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) #one_time чтобы пряталась клавиатура

kb_client.add(b1).add(b2).insert(b3) #row,start,add для компоновки кнопок