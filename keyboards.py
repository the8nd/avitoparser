from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

add_new_keyboard, delete_url_keyboard = KeyboardButton('Добавить'), KeyboardButton('Удалить')
check_all_keyboard, status_check_keyboarb = KeyboardButton('Показать все'), KeyboardButton('Изменить статус')

start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_keyboard.add(add_new_keyboard, delete_url_keyboard, check_all_keyboard, status_check_keyboarb)

cancel_button = KeyboardButton('/cancel')
cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
cancel_keyboard.add(cancel_button)