a_price = [0]
a_time = [0]
a_size = [0]

class New_test:

    def trade(self, symbol, side, type, size, price, time):
        global a_price
        global a_time
        global a_size

        a_price.append(price)
        a_time.append(time)
        if side == "SIDE_BUY":
            a_size.append(size)
        elif side == "SIDE_SELL":
            a_size.append(-size)

    def priced(self):
        return a_price
    def timed(self):
        return a_time
    def sized(self):
        return a_size
    def position(self):
        return sum(a_size)
    def entry(self):
        p = self.position()
        y = -1
        x = 0
        entry = 0
        while x != (p):
            entry += (a_size[y] / p * a_price[y])
            x += a_size[y]
            y -= 1
        return entry

                                    
