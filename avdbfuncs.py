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
        last_links = '\m/'.join([first_update[0][counter] for counter in range(3)])
        last_links_update = db.update(urls_base).where(urls_base.columns.user_id == user_id,urls_base.columns.url_id == f_url[1]).values(last_urls=last_links)
        connection.execute(last_links_update)
        connection.commit()


def db_get_all(user_id):
    get_all = db.select(urls_base.columns.url_id, urls_base.columns.url,
                        urls_base.columns.url_name, urls_base.columns.status).where(urls_base.columns.user_id==user_id)
    get_all_result = connection.execute(get_all)
    final_all = get_all_result.fetchall()
    msg_for_return = ''
    for i, inf in enumerate(final_all):
        msg_for_return = msg_for_return + f'url id: {inf[0]}\n{hlink(inf[2], inf[1])}\nstatus: {inf[3]}\n'
        msg_for_return = msg_for_return + f"<b>─</b>"*25 + '\n'
    return msg_for_return


# 0 - url_name, 1 - url, 2 - last_url, 3 - url_id
# avcheck[1], 0, 1, 2 - last url, 3 - url, 4 - url_name
async def urls_check(user_id: int):
    url_check = db.select(urls_base.columns.url_name, urls_base.columns.url, urls_base.columns.last_urls,
                          urls_base.columns.url_id).where(urls_base.columns.status == True, urls_base.columns.user_id == user_id)
    url_check_f = connection.execute(url_check)
    for j, inf_url in enumerate(url_check_f.fetchall()):
        url_avcheck = await avparser(inf_url[1])
        try:
            last_url_unpack = inf_url[2].split('\m/')
        except AttributeError:
            logging.info('AttrErr')
        if url_avcheck[0] != last_url_unpack:
            logging.info(f'{user_id} alert {datetime.datetime.now()}')
            #print(f'url_avcheck[0]:{url_avcheck[0]}')
            #print(f'luu before append:{last_url_unpack}')
            url_avcheck[0].append(inf_url[1])
            url_avcheck[0].append(inf_url[0])
            last_links = '\m/'.join([url_avcheck[0][counter] for counter in range(3)])
            last_links_update = db.update(urls_base).where(urls_base.columns.user_id == user_id,
                                                           urls_base.columns.url_id == inf_url[3]).values(last_urls=last_links)
            connection.execute(last_links_update)
            connection.commit()
            yield url_avcheck[0], url_avcheck[1]


def create_message(data) -> str:
    msg_to_return = ''.join([hlink(data[1][i], data[0][i]) + f'\n{str(f"<b>{spacer_creater()}</b>")}\n' for i in range(3)] + [hlink(data[0][4], data[0][3])])
    print(msg_to_return)
    return msg_to_return


def spacer_creater():
    return '─'*25
