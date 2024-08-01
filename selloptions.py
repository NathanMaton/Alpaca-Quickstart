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

def job2():
    # A few of the other types of things I tried here are left as comments below.
    # market_buy_sell_stock("SPY", 1, 'buy', client)
    # market_buy_sell_option("VXX240719C00012500", 1, 'buy', client)
    # long_strangle('AAPL', 1, 'buy', 5, client)
    sell_options(client)

job2()