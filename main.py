import asyncio
import logging
from parser import parser
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot_token import token

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot=bot, storage=storage)

logging.basicConfig(filename='av_info.log', encoding='utf-8', level=logging.INFO)


# Проверяем изменение первых 3-х ссылок. Изменились - оповещаем пользователя
async def main(msg, url):
    main_links = parser(url)
    while True:
        a = parser(url)
        logging.info(f'{main_links} main all')
        if a != main_links:
            msg_all = ''
            logging.info(f'{a} a if')
            logging.info('alert')
            for i, inf in enumerate(a):
                msg_all = msg_all + f'{inf}\n{str("<b>─</b>")*25}\n'
            await bot.send_message(msg.from_user.id, msg_all + url, parse_mode='HTML')
            main_links = a
        log = f'{a} after if'
        logging.info(log)
        logging.info('-'*20)
        await asyncio.sleep(30)


# Приветственное сообщение
@dp.message_handler(commands=['start'])
async def start_command(msg: types.Message):
    await msg.reply(("Отправь ссылку"))
    logging.info(msg.from_user.username)
    logging.info(msg.from_user.id)


# Принимаем ссылку пользователя и вызываем функцию обработки
@dp.message_handler()
async def alert_sender(msg: types.Message):
    url = msg.text
    data = await main(msg, url)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
