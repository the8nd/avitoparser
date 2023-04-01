import asyncio
import logging
import sqlalchemy as db
from keyboards import start_keyboard, cancel_keyboard
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageTextIsEmpty
from bot_token import token
from avdbfuncs import urls_base, connection, db_get_all
from avdbfuncs import urls_check, create_message, first_check

storage = MemoryStorage()
bot = Bot(token=token)
dp = Dispatcher(bot=bot, storage=storage)

logging.basicConfig(filename='av_info.log', encoding='utf-8', level=logging.INFO)


class ClientStatesGroup(StatesGroup):
    add_new_url = State()
    add_new_name = State()
    delete_url = State()
    change_url_status = State()


#move to main and add user id to urls_check call
async def looped_send_msg(user_id):
    while True:
        async for data in urls_check(user_id):
            await bot.send_message(user_id, create_message(data), parse_mode='HTML')
        await asyncio.sleep(30)


@dp.message_handler(commands=['cancel'], state='*')
async def cancel_command(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await msg.reply('Отменил.\nВыберите новое действие.', reply_markup=start_keyboard)
    await state.finish()


@dp.message_handler(commands=['start'])
async def start_command(msg: types.Message):
    await msg.reply("Выбери нужную опцию:\n- Добавить URL\n"
                     "- Удалить URL\n"
                     "- Изменить статус URL\n"
                     "- Отобразить все URL", reply_markup=start_keyboard)
    logging.info(msg.from_user.username)
    logging.info(msg.from_user.id)
    url_update = await first_check(msg.from_user.id)
    loop = await looped_send_msg(msg.from_user.id)


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
async def url_delete_start(msg: types.Message, state: FSMContext):
    await ClientStatesGroup.delete_url.set()
    user_id = msg.from_user.id
    all_urls = db_get_all(user_id)
    try:
        await msg.answer(all_urls, parse_mode='HTML')
        await msg.answer('Отправь url id, чтобы я удалил его', reply_markup=cancel_keyboard)
    except MessageTextIsEmpty:
        await msg.answer('У вас нет добавленных URL')
        await state.finish()



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
    try:
        await msg.answer(get_info, parse_mode='HTML')
    except MessageTextIsEmpty:
        await msg.answer('У вас нет добавленных URL')


@dp.message_handler(Text(equals='Изменить статус', ignore_case=True), state=None)
async def status_change_start(msg: types.Message, state: FSMContext):
    await ClientStatesGroup.change_url_status.set()
    user_id = msg.from_user.id
    all_urls = db_get_all(user_id)
    try:
        await msg.answer(all_urls, parse_mode='HTML')
        await msg.answer('Отправь url id для изменения статуса', reply_markup=cancel_keyboard)
    except MessageTextIsEmpty:
        await msg.answer('У вас нет добавленных URL')
        await state.finish()


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
