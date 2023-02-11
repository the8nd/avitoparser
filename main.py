import asyncio
import logging
import sqlalchemy as db
from avparser import avparser
from keyboards import start_keyboard, cancel_keyboard
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hlink

from bot_token import token

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot=bot, storage=storage)

logging.basicConfig(filename='av_info.log', encoding='utf-8', level=logging.INFO)

engine = db.create_engine('sqlite:///urls_base.db')
connection = engine.connect()
metadata = db.MetaData()


class ClientStatesGroup(StatesGroup):
    add_new_url = State()
    add_new_name = State()
    delete_url = State()
    change_url_status = State()


urls_base = db.Table('urls_base', metadata,
                     db.Column('url_id', db.Integer, primary_key=True, autoincrement=True),
                     db.Column('user_id', db.Integer),
                     db.Column('url', db.Text),
                     db.Column('url_name', db.Text),
                     db.Column('last_urls', db.Text),
                     db.Column('status', db.Boolean)
                     )
metadata.create_all(engine)


def db_get_all(user_id):
    get_all = db.select(urls_base.columns.url_id, urls_base.columns.url, urls_base.columns.url_name, urls_base.columns.status).where(urls_base.columns.user_id==user_id)
    get_all_result = connection.execute(get_all)
    final_all = get_all_result.fetchall()
    msg_for_return = ''
    for i, inf in enumerate(final_all):
        msg_for_return = msg_for_return + f'url id: {inf[0]}\n{hlink(inf[2], inf[1])}\nstatus: {inf[3]}\n'
        msg_for_return = msg_for_return + f"<b>─</b>"*25 + '\n'
    return msg_for_return


@dp.message_handler(commands=['cancel'], state='*')
async def cancel_command(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await msg.reply('Отменил.\nВыберите новое действие.', reply_markup=start_keyboard)
    await state.finish()


# Проверяем изменение первых 3-х ссылок. Изменились - оповещаем пользователя
async def urls_check():
    first_check = db.select(urls_base.columns.user_id, urls_base.columns.url_id, urls_base.columns.url).where(urls_base.columns.status == True)
    first_check_f = connection.execute(first_check)
    for i, url_one in enumerate(first_check_f.fetchall()):
        url_check = await avparser(url_one[2])
        last_url_one = ''
        counter = 0
        for i_ in range(3):
            last_url_one = last_url_one + f'{url_check[0][counter]}\m/'
            counter +=1
        last_url_upd = db.update(urls_base).where(urls_base.columns.user_id == url_one[0], urls_base.columns.url_id == url_one[1]).values(last_urls = last_url_one)
        connection.execute(last_url_upd)
        connection.commit()
        await asyncio.sleep(2)
    while True:
        loop_url_chekc = db.select(urls_base.columns.user_id, urls_base.columns.url_name, urls_base.columns.url, urls_base.columns.last_urls, urls_base.columns.url_id).where(urls_base.columns.status == True)
        loop_url_chekc_f = connection.execute(loop_url_chekc)
        for j, inf_url in enumerate(loop_url_chekc_f.fetchall()):
            loop_parser = await avparser(inf_url[2])
            last_url_unpacked = inf_url[3].split('\m/')
            last_url_unpacked.pop(3)
            if loop_parser[0] != last_url_unpacked:
                msg_to_send = ''
                for i, inf in enumerate(loop_parser[0]):
                    msg_to_send = msg_to_send + hlink(loop_parser[1][i], inf) + f'\n{str("<b>─</b>") * 25}\n'
                await bot.send_message(inf_url[0], msg_to_send + hlink(inf_url[1], inf_url[2]), parse_mode='HTML')
                last_links = ''
                counter_ = 0
                for i_ in range(3):
                    last_links = last_links + f'{loop_parser[0][counter_]}\m/'
                    counter_ += 1
                last_links_update = db.update(urls_base).where(urls_base.columns.user_id == inf_url[0], urls_base.columns.url_id == inf_url[4]).values(last_urls=last_links)
                connection.execute(last_links_update)
                connection.commit()
                await asyncio.sleep(2)
        await asyncio.sleep(20)


@dp.message_handler(commands=['start'])
async def start_command(msg: types.Message):
    await msg.reply("Выбери нужную опцию:\n- Добавить URL\n"
                     "- Удалить URL\n"
                     "- Изменить статус URL\n"
                     "- Отобразить все URL", reply_markup=start_keyboard)
    loop = await urls_check()
    logging.info(msg.from_user.username)
    logging.info(msg.from_user.id)


@dp.message_handler(Text(equals='Добавить', ignore_case=True), state=None)
async def url_adding_start(msg: types.Message):
    await ClientStatesGroup.add_new_name.set()
    await msg.answer('Укажите имя для ссылки.', reply_markup=cancel_keyboard)


@dp.message_handler(state=ClientStatesGroup.add_new_name)
async def url_name_add(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = msg.text
    await msg.answer('Отправь URL. Не забудь выбрать сортировку по дате на авито.', reply_markup=cancel_keyboard)
    await ClientStatesGroup.add_new_url.set()


@dp.message_handler(state=ClientStatesGroup.add_new_url)
async def url_adding_finish(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url'] = msg.text
    user_id = msg.from_user.id
    insert = urls_base.insert().values([
        {'user_id': user_id, 'url': data['url'], 'url_name': data['name'], 'status': True}
    ])
    connection.execute(insert)
    connection.commit()
    await msg.answer('Добавил. Можете проверить по кнопке "Показать все".', reply_markup=start_keyboard)
    await state.finish()


@dp.message_handler(Text(equals='Удалить', ignore_case=True), state=None)
async def url_delete_start(msg: types.Message):
    await ClientStatesGroup.delete_url.set()
    user_id = msg.from_user.id
    all_urls = db_get_all(user_id)
    await msg.answer(all_urls, parse_mode='HTML')
    await msg.answer('Отправь url id, чтобы я удалил его', reply_markup=cancel_keyboard)


@dp.message_handler(state=ClientStatesGroup.delete_url)
async def url_delete_finish(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    url_id = msg.text
    delete_url = db.delete(urls_base).where(urls_base.columns.url_id == url_id, urls_base.columns.user_id == user_id)
    connection.execute(delete_url)
    connection.commit()
    await msg.answer('Удалил. Можете проверить результат по кнопке "Показать все".', reply_markup=start_keyboard)
    await state.finish()


@dp.message_handler(Text(equals='Показать все', ignore_case=True), state=None)
async def show_all_url(msg: types.Message):
    user_id = msg.from_user.id
    get_info = db_get_all(user_id)
    await msg.answer(get_info, parse_mode='HTML')


@dp.message_handler(Text(equals='Изменить статус', ignore_case=True), state=None)
async def status_change_start(msg: types.Message):
    await ClientStatesGroup.change_url_status.set()
    user_id = msg.from_user.id
    all_urls = db_get_all(user_id)
    await msg.answer(all_urls, parse_mode='HTML')
    await msg.answer('Отправь url id для изменения статуса', reply_markup=cancel_keyboard)


@dp.message_handler(state=ClientStatesGroup.change_url_status)
async def status_change_finish(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    url_id = msg.text
    status = True
    check_status = db.select(urls_base.columns.status).where(urls_base.columns.url_id == url_id, urls_base.columns.user_id==user_id)
    check_status_f = connection.execute(check_status)
    if check_status_f.fetchall()[0][0]:
        status = False
    upd_status = db.update(urls_base).where(urls_base.columns.url_id == url_id, urls_base.columns.user_id == user_id).values(status = status)
    connection.execute(upd_status)
    connection.commit()
    await msg.answer('Изменил. Проверить можно по кнопке "Показать все"', reply_markup=start_keyboard)
    await state.finish()


# Принимаем ссылку пользователя и вызываем функцию обработки
@dp.message_handler()
async def all_msg(msg: types.Message):
    await msg.answer('Не понял команду. Попытайтесь снова.')
    print_all = db.select(urls_base)
    all_pr = connection.execute(print_all)
    print(all_pr.fetchall())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
