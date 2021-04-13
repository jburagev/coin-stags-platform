import numpy as np

class BuyLowSellHigh:

    def calculateVolume(self, current_volume):
        return current_volume

    def calculateUsd(self, current_usd):
        return current_usd

    def decide(self, row):
        if row["isCurrentMax"]:
            return 'SELL'
        elif row["isCurrentMin"]:
            return 'BUY'
        else:
            return 'HOLD'

    def __str__(self):
        return __class__.__name__
