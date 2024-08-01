'''
looks at open positions, outputs dataframe of p&ls
'''

import pandas as pd
from alpaca.trading.client import TradingClient
import os

api_key = 'PKP10JHCPSOHDH3FUBPU'
secret = os.environ['secret']


#set up logs
import logging
logging.basicConfig(
    filename='alpaca_trades.log',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger('test')

def evaluate_pl():
    PROFIT_THRESHOLD = 100
    
    trade_client = TradingClient(api_key, secret, paper=True)
    positions = trade_client.get_all_positions()
    # print (positions[0])
    classes =[x.asset_class for x in positions] 
    symbols = [x.symbol for x in positions]
    qty = [x.qty for x in positions]
    # expirations = [x.expiration_date for x in positions]
    pls = [x.unrealized_pl for x in positions]
    dict = {'symbols': symbols, 'classes': classes, 'quantity': qty, 'pls': pls} 
    df = pd.DataFrame(dict)
    symbols_to_sell = []
    for i, pnl in enumerate(pls):
        if float(pnl) > PROFIT_THRESHOLD:
            symbols_to_sell.append(symbols[i])
            # eventually add code to sell.
            # market_buy_sell_option(symbols[i], 1, 'sell', trade_client)
    if len(symbols_to_sell)>0:
        print (f'{symbols_to_sell} are options are abvove the profit threshold of {PROFIT_THRESHOLD}')


    return df, symbols_to_sell

if __name__ == "__main__":
    df, symbols_to_sell =evaluate_pl()
    print (df, symbols_to_sell)
