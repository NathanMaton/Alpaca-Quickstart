'''Functions to buy stocks and options in Alpaca
'''

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOptionContractsRequest, AssetStatus
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce
import os
import requests
import json
import math
from evaluate import evaluate_pl
import datetime

#set up logs
import logging
logging.basicConfig(
    filename='alpaca_trades.log',
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger('test')

api_key = 'PKP10JHCPSOHDH3FUBPU'
secret = os.environ['secret']

def auth():
    return TradingClient(api_key, secret, paper=True)

def get_latest_stock_price(symbol):
    # you can do some of this in Alpaca, but I found this API easier
    url = f"https://data.alpaca.markets/v2/stocks/quotes/latest?symbols={symbol}"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret
    }

    response = requests.get(url, headers=headers)

    price = json.loads(response.text)['quotes'][f'{symbol}']['bp']
    time = json.loads(response.text)['quotes'][f'{symbol}']['t']
    return price, time 

def create_market_order(symbol, qty, action, type):
    if type == 'stock' and action == 'buy':
        req = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                    )
    if type == 'stock' and action == 'sell':
        req = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                    )
    if type == 'option' and action == 'buy':
        req = MarketOrderRequest(
            symbol = symbol,
            qty = qty,
            side = OrderSide.BUY,
            type = OrderType.MARKET,
            time_in_force = TimeInForce.DAY,
        )
    if type == 'option' and action == 'sell':
        req = MarketOrderRequest(
            symbol = symbol,
            qty = qty,
            side = OrderSide.SELL,
            type = OrderType.MARKET,
            time_in_force = TimeInForce.DAY,
        )
    if type == 'crypto' and action == 'buy':
        req = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.GTC
                    )
    if type == 'crypto' and action == 'sell':
        req = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.GTC
                    )
    return req

def trade_crypto(symbol, qty, action, client):
    # preparing market order
    req = create_market_order(symbol, qty, action, 'crypto')
    res = client.submit_order(req)
    print(f'crypto {action} order for {qty} of {symbol} submitted')
    logger.info(f'crypto {action} order for {qty} of {symbol} submitted')

def market_buy_sell_stock(symbol, qty, action, client):
    # preparing market order
    req = create_market_order(symbol, qty, action, 'stock')
    res = client.submit_order(req)
    print(f'stock {action} order submitted')
    logger.info(f'stock {action} order submitted')

def market_buy_sell_option(symbol, qty, action, client):
    req = create_market_order(symbol, qty, action, 'option')
    res = client.submit_order(req)
    print(f'option {action} order submitted for {qty} of {symbol}')
    logger.info(f'option {action} order submitted for {qty} of {symbol}')

def sell_profitable_options(client):
    df, symbols_to_sell = evaluate_pl()
    for symbol in symbols_to_sell:
        market_buy_sell_option(symbol, 1, 'sell', client)

def sell_options(client):
    df, symbols_to_sell = evaluate_pl()
    options = df.loc[df['classes'] == "us_option"]
    for index, row in options.iterrows():
        market_buy_sell_option(row['symbols'], row['quantity'], 'sell', client)

    # for symbol in options.symbols:
    #     market_buy_sell_option(symbol, 1, 'sell', client)


def get_options_contracts(symbol, put_sp, call_sp, client):
    underlying_symbols = [f'{symbol}']


    today = datetime.date.today()
    friday = today + datetime.timedelta( (4-today.weekday()) % 7 )
    format="%Y-%m-%d"

    req = GetOptionContractsRequest(
        underlying_symbols = underlying_symbols,               # specify underlying symbols
        status = AssetStatus.ACTIVE,                           # specify asset status: active (default)
        expiration_date = friday.strftime(format),                        # specify expiration date (specified date + 1 day range)
    #    expiration_date = '2024-08-16',                        # specify expiration date (specified date + 1 day range)
        expiration_date_gte = None,                            # we can pass date object
        expiration_date_lte = None,                            # or string (YYYY-MM-DD)
        root_symbol = None,                                    # specify root symbol
        type = None,                                           # specify option type (ContractType.CALL or ContractType.PUT)
        style = None,                                          # specify option style (ContractStyle.AMERICAN or ContractStyle.EUROPEAN)
        strike_price_gte = str(put_sp-1),                               # specify strike price range
        strike_price_lte = str(call_sp+1),                               # specify strike price range
        limit = 100,                                             # specify limit
        page_token = None,                                     # specify page token
    )
    return client.get_option_contracts(req)

def get_strangle_contract_symbols(res, put_sp, call_sp):
    put_to_buy = 0
    call_to_buy = 0 
    clean_data = 0
    for contract in res.option_contracts:
        if contract.strike_price == put_sp and contract.type.split(' ')[0] == 'put':
            put_to_buy = contract.symbol
            clean_data += 1 
        if contract.strike_price == call_sp and contract.type.split(' ')[0] == 'call':
            call_to_buy = contract.symbol
            clean_data += 1
            
    if clean_data == 2:
        return put_to_buy, call_to_buy
        

    # data is not easy in APPL example I'm working on
    # look for nearby strike price contracts for puts and calls
    strike_prices = [contract.strike_price for contract in res.option_contracts]
    closest_put_sp = min(strike_prices, key=lambda x:abs(x-put_sp))
    closest_call_sp = min(strike_prices, key=lambda x:abs(x-call_sp))

    # look up contract symbol for that strike price
    for contract in res.option_contracts:
        if contract.strike_price == closest_put_sp and contract.type.split(' ')[0] == 'put':
            put_to_buy = contract.symbol
        if contract.strike_price == closest_call_sp and contract.type.split(' ')[0] == 'call':
            call_to_buy = contract.symbol
    return put_to_buy, call_to_buy


def long_strangle(symbol, qty, action, spread, client):
    '''
    ## TODO: write nice function definition 
    find the right options given a symbol, then do buy
    '''

    # get price of asset - vixy 10.65
    current_stock_price, time = get_latest_stock_price(symbol)

    # get relevant options contracts
    put_sp = math.floor(current_stock_price - spread)
    call_sp = math.floor(current_stock_price + spread)
    res = get_options_contracts(symbol, put_sp, call_sp, client)

    # find contracts of the spread amount around asset 
    put_to_buy, call_to_buy = get_strangle_contract_symbols(res, put_sp, call_sp)
    
    # make purchases.
    market_buy_sell_option(put_to_buy, qty, action, client)
    market_buy_sell_option(call_to_buy, qty, action, client)


if __name__ == "__main__":
    client = auth()
    # trade_crypto("DOGEUSD", 9.975, 'buy', client)
    # market_buy_sell_option("VIXY240719C00012500", 1, 'sell', client)
    #long_strangle('AAPL', 1, 'buy', 5, client)
    market_buy_sell_stock('VOO', 95, 'buy', client)
    long_strangle('TSLA', 1, 'buy', 2, client)
    #long_strangle('NVDA', 1, 'buy', 2, client)
    # sell_profitable_options(client)
    # sell_options(client)