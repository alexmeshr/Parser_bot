import datetime
from datetime import time, date, datetime, timedelta
import aiofiles
from asyncio import sleep
from Database.db_requests import get_ids, update_schedule_table
from PDF_parsing.Sarov_parser import parse_msu_website
from PDF_parsing.pdf_parser import parse_pdf
from PDF_parsing.Day_schedule import *
import bot_init
import os

async def db_updator(delay:int = 18000):
    """Updates db by shedule

        delay: delay in seconds default 5h
    """
    print(datetime.now().__str__(), " : db_updator ")
    while True:
        await sleep(delay)
        response = await upd_db()
        response = "BOT MANAGER DB UPDATED" if response else "BOT MANAGER NOT RESPONDING"
        print(response)


async def schedule_updator(update_time=time.fromisoformat('05:00:00')):
    print(datetime.now().__str__(), " : scedule_updator ")
    while True:
        #ВЕРНУТЬ
        ###parse_msu_website(bot_init.PDF_PATH)
        nearest_scedule = {(datetime.today().timetuple().tm_yday + i): [] for i in
                           range(14 - datetime.today().weekday())}
        for f in os.listdir(bot_init.PDF_PATH):
            print(f)
            try:
                parse_pdf(nearest_scedule, bot_init.PDF_PATH + f, bot_init.groups, logging=False)
            except Exception as e:
                print(e)
        update_schedule_table(nearest_scedule)
        dh = update_time.hour - datetime.now().hour
        dh = dh+24 if dh <= 0 else dh
        dm = update_time.minute - datetime.now().minute
        dm = dm+60 if dm <= 0 else dm
        ds = update_time.second - datetime.now().second
        ds = ds + 60 if ds <= 0 else ds
        delay = timedelta(hours=dh,minutes=dm,seconds=ds).total_seconds()
        print(dh, dm, ds, delay)
        await sleep(delay)


async def upd_db(notify_id:int=235717130, mode:int=0):
    users = get_ids()
    async with aiofiles.open('db.txt', 'wb') as f:
        for u in users:
            await f.write(bytes(str(u[0])+"\n","UTF-8"))
    return True
