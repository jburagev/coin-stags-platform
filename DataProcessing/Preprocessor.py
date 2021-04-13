import sys
import numpy as np
from datetime import datetime

import pandas

from Strategies.StrategySelector import StrategySelector

class Preprocessor:

    data = []


    def assignClassByStrategy(self, data, strategy):

        strategyClass = StrategySelector().select(strategy)
        actions_buy = []
        actions_sell = []
        actions_hold = []
        prev_actions = []
        prev_action = 1

        for date, row in data.iterrows():
            decidedClass = strategyClass.decide(row)
            if decidedClass == "BUY":
                actions_buy.append(1)
                actions_sell.append(0)
                actions_hold.append(0)
                prev_actions.append(prev_action)
                prev_action = 0
            elif decidedClass == "SELL":
                actions_buy.append(0)
                actions_sell.append(1)
                actions_hold.append(0)
                prev_actions.append(prev_action)
                prev_action = 1
            else:
                actions_buy.append(0)
                actions_sell.append(0)
                actions_hold.append(1)
                prev_actions.append(prev_action)

        data['action_buy'] = actions_buy
        data['action_sell'] = actions_sell
        data['action_hold'] = actions_hold
        data['prev_action'] = prev_actions

        return data

    def calculateIsMaxColumn(self, data, column, interval):
        batches = Preprocessor.batch(data, interval)
        resultData = []
        for batch in batches:
            maxVal = sys.float_info.min
            # Find max
            for date, row in batch.iterrows():
                if float(row[column]) > maxVal:
                    maxVal = float(row[column])

            # Set if current max
            maxSet = False
            for date, row in batch.iterrows():
                if float(row[column]) == maxVal and not maxSet:
                    row["isCurrentMax"] = 1
                    maxSet = True
                else:
                    row["isCurrentMax"] = 0
                resultData.append(row["isCurrentMax"])

        data["isCurrentMax"] = resultData

        return resultData

    def calculateIsMinColumn(self, data, column, interval):

        batches = Preprocessor.batch(data, interval)
        resultData = []
        for batch in batches:
            minVal = sys.float_info.max
            # Find min
            for date, row in batch.iterrows():
                if float(row[column]) < minVal:
                    minVal = float(row[column])

            # Set if current min
            minSet = False
            for date, row in batch.iterrows():
                if float(row[column]) == minVal and not minSet:
                    row["isCurrentMin"] = 1
                    minSet = True
                else:
                    row["isCurrentMin"] = 0
                resultData.append(row["isCurrentMin"])

        data["isCurrentMin"] = resultData

        return resultData

    @staticmethod
    def batch(data, n=1):
        #grouping data by n. If its 12 means that 12 samples of data are batched toghether.
        for g, df in data.groupby(np.arange(len(data)) // n):
            yield df

    @staticmethod
    def dateparse(timestamp):
        if len(timestamp) == 19:
            timestamp = int(timestamp)/10**9
        elif len(timestamp) == 10:
            timestamp = int(timestamp)
        else:
            raise Exception('Invalid timestamp format')

        return datetime.fromtimestamp(timestamp)

    @staticmethod
    def load_dataset(csv_filename):
        with open(csv_filename) as csv_file:
            df = pandas.read_csv(csv_file, parse_dates=True, date_parser=Preprocessor.dateparse, index_col='Timestamp')

            return df

    def write(self, df, subdir="", add_sanitization_suffix=False, mode="w", header=True,csv_filename='test'):
        df.index = df.index.astype(int)
        filepath = 'data/preprocessed/' + csv_filename + '.csv'
        df.to_csv(index=True, header=header, path_or_buf=filepath, mode=mode)