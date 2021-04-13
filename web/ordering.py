from binance.enums import *
from binance.client import Client

client = Client()

class New_order:
    def __init__(self, key, secret):
        global client
        client = Client(key, secret, tld = 'com')

    def trade(self, symbol, side, type, quantity, price, time):
        global client
        if type == "ORDER_TYPE_MARKET":
            try:
                order = client.create_order(
                symbol=symbol,
                side=side,
                type=type,
                #timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                #price=price
                )
            except Exception as e:
                #print(e.message, "error")
                print("Error: {0}".format(e))
        elif type == "ORDER_TYPE_LIMIT":
            try:
                order = client.create_order(
                symbol=symbol,
                side=side,
                type=type,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                price=price
                )
            except Exception as e:
                #print(e.message, "error")
                print("Error: {0}".format(e))                      
