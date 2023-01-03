import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('API_KEY')

headers = {
    'x-api-key': api_key,
    'Content-Type': 'application/json',
}


def query_pool_balance(pool_address):
    json_data = {
        'sql': "WITH pool AS ( SELECT dp.contract_address, token_address AS token_address FROM ethereum.dex_pools dp CROSS JOIN unnest(token_addresses) as token_address WHERE dp.contract_address = '{{pool_address}}' ) SELECT symbol, pool_balance, pool_balance/SUM(pool_balance) OVER ( PARTITION BY  1) as pool_percentage FROM pool LEFT JOIN LATERAL ( SELECT (SELECT symbol FROM ethereum.tokens tk WHERE dl.token_address = tk.contract_address) as symbol, pool_balance / POW(10, (SELECT decimals FROM ethereum.tokens tk WHERE dl.token_address = tk.contract_address)) AS pool_balance FROM ethereum.dex_liquidity dl WHERE dl.contract_address = pool.contract_address AND dl.token_address = pool.token_address ORDER BY timestamp desc LIMIT 1 ) dl ON true",
        'parameters': {
            'pool_address': pool_address,
        },
        'options': {},
    }
    response = requests.post('https://api.transpose.io/sql', headers=headers, json=json_data)
    return response.json()
