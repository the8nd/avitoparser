from avparser import avparser
import sqlalchemy as db
import logging
import datetime
from aiogram.utils.markdown import hlink

engine = db.create_engine('sqlite:///urls_base.db')
connection = engine.connect()
metadata = db.MetaData()


urls_base = db.Table('urls_base', metadata,
                     db.Column('url_id', db.Integer, primary_key=True, autoincrement=True),
                     db.Column('user_id', db.Integer),
                     db.Column('url', db.Text),
                     db.Column('url_name', db.Text),
                     db.Column('last_urls', db.Text),
                     db.Column('status', db.Boolean)
                     )
metadata.create_all(engine)


async def first_check(user_id):
    first_url_check = db.select(urls_base.columns.url, urls_base.columns.url_id).where(urls_base.columns.status == True, urls_base.columns.user_id == user_id)
    first_url_check_f = connection.execute(first_url_check)
    for o, f_url in enumerate(first_url_check_f.fetchall()):
        first_update = await avparser(f_url[0])
        last_links = ''
        counter = 0
        for i in range(3):
            last_links = last_links + f'{first_update[0][counter]}\m/'
            counter += 1
        last_links_update = db.update(urls_base).where(urls_base.columns.user_id == user_id,urls_base.columns.url_id == f_url[1]).values(last_urls=last_links)
        connection.execute(last_links_update)
        connection.commit()


def db_get_all(user_id):
    get_all = db.select(urls_base.columns.url_id, urls_base.columns.url, urls_base.columns.url_name, urls_base.columns.status).where(urls_base.columns.user_id==user_id)
    get_all_result = connection.execute(get_all)
    final_all = get_all_result.fetchall()
    msg_for_return = ''
    for i, inf in enumerate(final_all):
        msg_for_return = msg_for_return + f'url id: {inf[0]}\n{hlink(inf[2], inf[1])}\nstatus: {inf[3]}\n'
        msg_for_return = msg_for_return + f"<b>─</b>"*25 + '\n'
    return msg_for_return


# 0 - url_name, 1 - url, 2 - last_url, 3 - url_id
# last_url_unpack, 0, 1, 2 - last url, 3 - url, 4 - url_name
async def urls_check(user_id: int):
    url_update = await first_check(user_id)
    print('url check after upd')
    url_check = db.select(urls_base.columns.url_name, urls_base.columns.url, urls_base.columns.last_urls, urls_base.columns.url_id).where(urls_base.columns.status == True, urls_base.columns.user_id == user_id)
    url_check_f = connection.execute(url_check)
    for j, inf_url in enumerate(url_check_f.fetchall()):
        print('----')
        print(inf_url)
        print('----')
        url_avcheck = await avparser(inf_url[1])
        try:
            last_url_unpack = inf_url[2].split('\m/')
            last_url_unpack.pop(3)
        except AttributeError:
            logging.info('AttrErr')
        if url_avcheck[0] != last_url_unpack:
            logging.info(f'{user_id} alert {datetime.datetime.now()}')
            last_url_unpack.append(inf_url[1])
            last_url_unpack.append(inf_url[0])
            print(last_url_unpack)
            # add links names to last_url_unpack
            last_links = ''
            counter = 0
            for i in range(3):
                last_links = last_links + f'{url_avcheck[0][counter]}\m/'
                counter += 1
            last_links_update = db.update(urls_base).where(urls_base.columns.user_id == user_id, urls_base.columns.url_id == inf_url[3]).values(last_urls=last_links)
            connection.execute(last_links_update)
            connection.commit()
            yield last_url_unpack, url_avcheck[1]


def create_message(data) -> str:
    msg_to_return = ''
    for i in range(3):
        msg_to_return = msg_to_return + hlink(data[1][i], data[0][i]) + f'\n{str("<b>─</b>")*25}\n'
    msg_to_return = msg_to_return + hlink(data[0][4], data[0][3])
    return msg_to_return



















#def db_get_all(user_id):
#    get_all = db.select(urls_base.columns.url_id, urls_base.columns.url, urls_base.columns.url_name, urls_base.columns.status).where(urls_base.columns.user_id==user_id)
#    get_all_result = connection.execute(get_all)
#    final_all = get_all_result.fetchall()
#    msg_for_return = ''
#    for i, inf in enumerate(final_all):
#        msg_for_return = msg_for_return + f'url id: {inf[0]}\n{hlink(inf[2], inf[1])}\nstatus: {inf[3]}\n'
#        msg_for_return = msg_for_return + f"<b>─</b>"*25 + '\n'
#    return msg_for_return
#
#
#async def urls_check():
#    first_check = db.select(urls_base.columns.user_id, urls_base.columns.url_id, urls_base.columns.url).where(urls_base.columns.status == True)
#    first_check_f = connection.execute(first_check)
#    for i, url_one in enumerate(first_check_f.fetchall()):
#        url_check = await avparser(url_one[2])
#        last_url_one = ''
#        counter = 0
#        for i_ in range(3):
#            last_url_one = last_url_one + f'{url_check[0][counter]}\m/'
#            counter +=1
#        last_url_upd = db.update(urls_base).where(urls_base.columns.user_id == url_one[0], urls_base.columns.url_id == url_one[1]).values(last_urls = last_url_one)
#        connection.execute(last_url_upd)
#        connection.commit()
#        await asyncio.sleep(2)
#    while True:
#        loop_url_chekc = db.select(urls_base.columns.user_id, urls_base.columns.url_name, urls_base.columns.url, urls_base.columns.last_urls, urls_base.columns.url_id).where(urls_base.columns.status == True)
#        loop_url_chekc_f = connection.execute(loop_url_chekc)
#        for j, inf_url in enumerate(loop_url_chekc_f.fetchall()):
#
#            loop_parser = await avparser(inf_url[2])
#            try:
#                last_url_unpacked = inf_url[3].split('\m/')
#                last_url_unpacked.pop(3)
#            except AttributeError:
#                pass
#            if loop_parser[0] != last_url_unpacked:
#                logging.info(f'{inf_url[0]} alert  {datetime.datetime.now()}')
#                msg_to_send = ''
#                for i, inf in enumerate(loop_parser[0]):
#                    msg_to_send = msg_to_send + hlink(loop_parser[1][i], inf) + f'\n{str("<b>─</b>") * 25}\n'
#                await bot.send_message(inf_url[0], msg_to_send + hlink(inf_url[1], inf_url[2]), parse_mode='HTML')
#                last_links = ''
#                counter_ = 0
#                for i_ in range(3):
#                    last_links = last_links + f'{loop_parser[0][counter_]}\m/'
#                    counter_ += 1
#                last_links_update = db.update(urls_base).where(urls_base.columns.user_id == inf_url[0], urls_base.columns.url_id == inf_url[4]).values(last_urls=last_links)
#                connection.execute(last_links_update)
#                connection.commit()
#                await asyncio.sleep(2)
#        await asyncio.sleep(45)
