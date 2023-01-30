import asyncio
import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot_token import token
from parser import *

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot=bot, storage=storage)

logging.basicConfig(filename='av_info.log', encoding='utf-8', level=logging.INFO)


async def main(msg, url):
    main_number = 0
    main_links = []
    check = parser(url)
    main_number = check[0]
    main_links = check[1]
    while True:
        a = parser(url)
        log = f'{main_number} - {main_links} main all'
        logging.info(log)
        if a[0] <= main_number and a[1] in main_links:
            main_number = a[0]
            main_links = a[1]
            log = f'{a[0]} - {a[1]} a if'
            logging.info(log)
        if a[0] >= main_number and a[1] not in main_links:
            msg_all = ''
            log = f'{a[0]} - {a[1]} a elif'
            logging.info(log)
            logging.info('alert')
            for i, inf in enumerate(a[1]):
                msg_all = msg_all + f'{inf}\n{str("<b>─</b>")*25}\n'
            await bot.send_message(msg.from_user.id, msg_all + url, parse_mode='HTML')
            main_number = a[0]
            main_links = a[1]
            msg_all = ''
        else:
            log = f'{a[0]} - {a[1]} else'
            logging.info(log)
        logging.info('-'*20)
        await asyncio.sleep(30)


@dp.message_handler(commands=['start'])
async def start_command(msg: types.Message):
    await msg.reply(("Отправь ссылку"))
    logging.info(msg.from_user.username)
    logging.info(msg.from_user.id)


@dp.message_handler()
async def alert_sender(msg: types.Message):
    url = msg.text
    data = await main(msg, url)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
