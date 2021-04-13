import time, json, talib, numpy #, pprint, pandas
import ta

#CCI_LENGTH = 20        #dolzina standardne deviacije in povprecja
#CCI_SOURCE = 'close'   #'close' ali 'open' ali 'high' ali 'low' - vir izracunov
CCI_LEVEL = 80          #limit CCI za nakup
DCA_LEVEL = 2.0         #prvi DCA level v odstotkih
DCA_POWER = 2           #mnogokratnik za vsak nadaljnji DCA level
TAKE_PROFIT = 2         #profit v odstotkih od vstopne cene

class Strategy():

    def find (self, x, y):
        #racunanje nivoja korena - order of root
        if (not(x > 0)):
            return 0
        elif (DCA_POWER**y==x):
            return y
        else:
            return (self.find (x, y+1))

    def feed(self, candles, open_orders, length, trade_size):

        #print('received feed')

        ####### MARKET in POZICIJE

        #print("input")
    
        position = float(open_orders['positionAmt'])
        entry = float(open_orders['entryPrice'])

        trade_size = float(trade_size)
        ma_list = candles
    
        ma_list = list(ma_list)
        ma_list = numpy.array(ma_list)
        ma = talib.SMA(ma_list, length)
        dev = talib.STDDEV(ma_list, length)


        cci = (numpy.add(ma_list, -ma)) / (0.015 * dev)

        ####### CONDITIONS

        #print("conditions")
    
        cond00 = True #on/off za trading

        cond10 = position == 0
    
        cond11 = cci[-1] < -abs(CCI_LEVEL)

        #print("position " + str(position) + " / trade_size " + str(trade_size))

        y = self.find(position / trade_size ,0)

        z = entry - (entry * ((DCA_LEVEL * DCA_POWER**y) * 0.01))

        z = round(z, 2)

        #print("cena DCA je : " + str(z))

        cond21 = ma_list[-1] < z

        cond22 = position < (trade_size * (DCA_LEVEL * DCA_POWER**y))

        cond_over = (ma_list[-1] > entry * (1+(TAKE_PROFIT*0.01))) and (position != 0)

        ####### TRADING

        #print("testing")

        if cond_over:
            #print("cond over")
            return -abs(position)

        elif cond00:
            if cond10 and cond11:
                #print("cci je " + str(cci[-1]))
                return trade_size
        
            elif cond11 and cond21 and cond22:
                #print("nov DCA pri " + str(z))
                return (1 * abs(position))
        else:
            #print("none")
            return

    def chart(self, candles, length):

        ma_list = candles
    
        ma_list = list(ma_list)
        ma_list = numpy.array(ma_list)
        ma = talib.SMA(ma_list, length)
        dev = talib.STDDEV(ma_list, length)

        cci = (numpy.add(ma_list, -ma)) / (0.015 * dev)

        return cci

