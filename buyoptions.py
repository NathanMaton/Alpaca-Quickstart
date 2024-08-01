import schedule
import time 
from evaluate import evaluate_pl
from trade import auth, sell_options, sell_profitable_options, long_strangle
import os
import pandas as pd
from alpaca.trading.client import TradingClient
import pandas as pd

api_key = 'PKP10JHCPSOHDH3FUBPU'
secret = os.environ['secret']
client = auth()

import logging
logging.basicConfig(
    filename='alpaca_trades.log',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger('test')

def job():
    #evaluate our portfolio
    df, symbols_to_sell = evaluate_pl()
    print(df)
    logger.info(df)

    #sell anything in the profits
    sell_profitable_options(client)

    #buy new strangles for the day
    long_strangle('TSLA', 2, 'buy', 2, client)

job()