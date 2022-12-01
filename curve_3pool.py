import os

import pandas as pd
import pytz
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import SyncWebhook
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()
mUrl = os.getenv('DISCORD')
api_key = os.getenv('API_KEY')


def curve_3pool():
    headers = {
        'x-api-key': api_key,
        'Content-Type': 'application/json',
    }
    json_data = {
        'sql': 'WITH wallet_tokens AS '
               '(  /* get all prev. owned tokens */ '
               'SELECT contract_address, balance '
               'FROM ethereum.token_owners '
               'WHERE owner_address = \'0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7\'  '
               'UNION ALL  /* get all live outbound tokens */ '
               '(SELECT contract_address, -1 * SUM(quantity) AS balance '
               'FROM ethereum.token_transfers '
               'WHERE from_address = \'0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7\' '
               'AND __confirmed = false '
               'GROUP BY contract_address)  '
               'UNION ALL  /* get all live inbound tokens */ '
               '(SELECT contract_address, SUM(quantity) AS balance '
               'FROM ethereum.token_transfers '
               'WHERE to_address = \'0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7\' '
               'AND __confirmed = false '
               'GROUP BY contract_address) ), '
               'token_information AS (     '
               'SELECT *     '
               'FROM ethereum.tokens     '
               'WHERE contract_address in (            '
               '\'0xdAC17F958D2ee523a2206206994597C13D831ec7\',            '
               '\'0x6B175474E89094C44Da98b954EedeAC495271d0F\',            '
               '\'0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48\'        '
               ') )  '
               'SELECT      '
               'symbol,     '
               'SUM(balance) /POW(10, decimals) AS balance '
               'FROM wallet_tokens '
               'LEFT JOIN token_information '
               'ON wallet_tokens.contract_address = token_information.contract_address '
               'WHERE wallet_tokens.contract_address in (            '
               '\'0xdAC17F958D2ee523a2206206994597C13D831ec7\',            '
               '\'0x6B175474E89094C44Da98b954EedeAC495271d0F\',            '
               '\'0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48\')  '
               'GROUP BY decimals, symbol;',
    }
    response = requests.post('https://api.transpose.io/sql', headers=headers, json=json_data)
    df = pd.DataFrame(response.json()['results'])
    df['percent'] = df['balance'] / sum(df['balance'])
    df['balance'] = df['balance'].astype(int)
    if len(df[(df.percent > 0.4) | (df.percent < 0.2)]):
        webhook = SyncWebhook.from_url(mUrl)
        webhook.send("```" + tabulate(df, tablefmt="simple_grid", headers=["token", "balance", "percent"],
                                      floatfmt=".2%", intfmt=',.0f', showindex='never') + "```")


if __name__ == "__main__":
    BKK = pytz.timezone("Asia/Bangkok")
    scheduler = BlockingScheduler()
    scheduler.add_job(curve_3pool, CronTrigger(timezone=BKK).from_crontab('*/15 * * * *'))
    scheduler.start()
