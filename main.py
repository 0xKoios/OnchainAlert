import os

import pandas as pd
import pytz
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import SyncWebhook
from dotenv import load_dotenv
from tabulate import tabulate
from query.transpose import query_pool_balance


def curve_pool():
    pool_address = {
        '3pool': '0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7',
        'busdv2': '0x4807862aa8b2bf68830e4c8dc86d0e9a998e085a',
        'busd': '0x79a8c46dea5ada233abaffd40f3a0a2b1e5a4f27'
    }
    for pool in pool_address:
        response = query_pool_balance(pool_address[pool])
        if response['status'] != 'success':
            pass
        df = pd.DataFrame(response['results'])
        print(df)
        # if len(df[(df.percent > 0.4) | (df.percent < 0.2)]):
        #     token = os.getenv('TG_BOT_TOKEN')
        #     bot_chat_id = os.getenv('TG_CHAT_ID')
        #     url = f'https://api.telegram.org/bot{token}/sendMessage?chat_id={bot_chat_id}&parse_mode=Markdown&text='
        #     message = '"token", "balance", "percent"'
        #     send_text = f'{url}{message}'
        #     requests.post(send_text)


if __name__ == "__main__":
    curve_pool()
    # BKK = pytz.timezone("Asia/Bangkok")
    # scheduler = BlockingScheduler()
    # scheduler.add_job(curve_3pool, CronTrigger(timezone=BKK).from_crontab('*/15 * * * *'))
    # scheduler.start()
