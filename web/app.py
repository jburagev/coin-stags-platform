from flask import Flask, escape, request, render_template, request, flash, redirect, jsonify, Response
import config

import ordering, testing, cci_in_dca_strategy_feed

from binance.client import Client
from binance.enums import *

app = Flask(__name__)
app.secret_key = b'8a7fds7tadf978gadfg879a98f7g'

LENGTH = 20
TRADE_SYMBOL = "BTCUSDT"
TRADE_SIDE = "SIDE_BUY"
TRADE_TYPE = "ORDER_TYPE_MARKET"
TRADE_SIZE = float(0.001)
TRADE_PRICE = float(0.0)

client = Client(config.API_KEY, config.API_SECRET, tld='com')
new_order = ordering.New_order(key = config.API_KEY, secret = config.API_SECRET)
new_test = testing.New_test()
new_strategy = cci_in_dca_strategy_feed.Strategy()

@app.route('/')
def index():
    title = 'CoinView'

    account_info = client.get_account()

    balances = account_info['balances']

    exchange_info = client.get_exchange_info()
    symbols = exchange_info['symbols']

    return render_template('index.html', title=title, my_balances = balances, symbols = symbols)

@app.route('/backtest')
def backtest():

    processed_candlesticks = hisdata()
    ma_list = []
    trade_time = []

    for data in processed_candlesticks:
        ma_list.append(float(data["close"]))
        trade_time.append(float(data["time"]))
            
    for x in range(LENGTH, len(ma_list)):

        open_orders = {
        "positionAmt":  new_test.position(),
        "entryPrice":   new_test.entry()
        }

        test_list = ma_list[x-LENGTH:x]

        #print(json.dumps(test_list, indent = 4))

        #print(open_orders["entryPrice"])
        reply = new_strategy.feed(test_list, open_orders, LENGTH, TRADE_SIZE)

        if reply:
            sided = ""
            if reply < 0:
                sided = "SIDE_SELL"
            elif reply > 0:
                sided = "SIDE_BUY"
            new_test.trade(symbol = TRADE_SYMBOL, side = sided, type = TRADE_TYPE, size = abs(reply), price = test_list[-1], time = trade_time[x])
        
    priced = new_test.priced()
    timed = new_test.timed()
    sized = new_test.sized()
    value = 0.0
    result = []

    for x in range(0,len(priced)):
        print(x)
        value = value + float(priced[x]) * float(-sized[x])
        candlestick = {
        "time":     timed[x],
        "value":    value
        }
        result.append(candlestick)

    return jsonify(result)

@app.route('/buy', methods=['POST'])
def buy():

    TRADE_SIDE = request.form['trade_side']
    TRADE_TYPE = request.form['trade_type']
    TRADE_SIZE = request.form['trade_size']
    TRADE_PRICE = request.form['trade_price']

    #print(request.form)

    try:
        order = new_order.trade(request.form['trade_symbol'],request.form['trade_side'],request.form['trade_type'],request.form['trade_size'],request.form['trade_price'],0)
    except Exception as e:
        flash(e.message, "error")

    return redirect('/')


@app.route('/input', methods=['POST'])
def input():

    global LENGTH

    print(request.form)
    
    TRADE_SYMBOL = request.form['trade_symbol']
    LENGTH = int(request.form['length'])

    return redirect('/')

def hisdata():
    candlesticks = client.get_historical_klines(TRADE_SYMBOL, Client.KLINE_INTERVAL_15MINUTE, "1 Jan, 2021")
    processed_candlesticks = []

    for data in candlesticks:
        candlestick = {
            "time":     data[0] / 1000,
            "open":     data[1],
            "high":     data[2],
            "low":      data[3],
            "close":    data[4],
            }

        processed_candlesticks.append(candlestick)

    return processed_candlesticks

@app.route('/history')
def history():
    processed_candlesticks = []
    
    processed_candlesticks = hisdata()

    return jsonify(processed_candlesticks)

@app.route('/strategy')
def strategy():
    candlesticks = client.get_historical_klines(TRADE_SYMBOL, Client.KLINE_INTERVAL_15MINUTE, "1 Jan, 2021")
    
    test_list = []
    time_list = []
    processed_candlesticks = []

    for data in candlesticks:
        test_list.append(float(data[4]))
        time_list.append(float(data[0]))

    reply = new_strategy.chart(candles = test_list, length =  LENGTH)

    for x in range (LENGTH,len(test_list)):
        candlestick = {
            "time":     time_list[x] / 1000,
            "value":    float(reply[x])
            }

        processed_candlesticks.append(candlestick)

    return jsonify(processed_candlesticks)

@app.route('/tick')
def tick():
    candlesticks = client.get_historical_klines(TRADE_SYMBOL, Client.KLINE_INTERVAL_15MINUTE, "1 Jan, 2021")

    test_list = []
    time = candlesticks[-1][0]

    for data in candlesticks:
        test_list.append(float(data[4]))

    reply = new_strategy.chart(candles = test_list, length =  LENGTH)

    candlestick = {
        "time":     time / 1000,
        "value":    float(reply[-1])
        }

    return candlestick

@app.route('/backtests')
def tick():
    candlesticks = client.get_historical_klines(TRADE_SYMBOL, Client.KLINE_INTERVAL_15MINUTE, "1 Jan, 2021")

    test_list = []
    time = candlesticks[-1][0]

    for data in candlesticks:
        test_list.append(float(data[4]))

    reply = new_strategy.chart(candles = test_list, length =  LENGTH)

    candlestick = {
        "time":     time / 1000,
        "value":    float(reply[-1])
    }

    return candlestick

app.run(host='0.0.0.0', port=5000)
