from poloniex import Poloniex
import requests
import pandas as pd
import os


class PoloniexDataLoader:

    dataSource = None
    csv_filename = ''


    def __init__(self, config,filename):
        self.dataSource = Poloniex(apikey=config["poloniex_api_key"], secret=config["poloniex_api_secret"])
        self.csv_filename = filename

    def fetchHistoricalData(self, url, currency_pair='USDT_ETH', start_timestamp=1439013600, end_timestamp=None,
                            period=86400, resolution='auto'):
        params = {
            'command': 'returnChartData',
            'currencyPair': currency_pair,
            'start': start_timestamp,
            'end': '9999999999',
            'period': period,
            'resolution': resolution
        }

        if end_timestamp is not None:
            params['end'] = end_timestamp

        end = False
        priceHistory = []

        lastTimestamp = 0
        while not end:
            ''' Poloniex api library is missing auto resolution so we need to perform retrieval by hand '''
            req = requests.get(url=url, params=params)
            print(url)
            print(params)
            data = req.json()

            for row in data:
                if row['date'] == 0:
                    end = True
                    break

                if int(row["date"]) > lastTimestamp:
                    lastTimestamp = int(row["date"])

                priceHistory.append(row)

            params['start'] = lastTimestamp + 1

        return self.convertJsonToDataframe(priceHistory)

    def write(self, df, subdir="", add_sanitization_suffix=False, mode="w", header=True,csv_filename='test'):
        df.index = df.index.astype(int)
        '''
        filename_parts = os.path.split(self.csv_filename)
        subdir_str = "/"
        if len(subdir) > 0:
            subdir_str = "/" + subdir + "/"
        filename = filename_parts[0] + subdir_str + filename_parts[1]
        if add_sanitization_suffix:
            filename = filename + self.stanizied_suffix
        '''
        filepath = 'data/price/' + csv_filename + '.csv'
        df.to_csv(index=True, header=header, path_or_buf=filepath, mode=mode)

    def convertJsonToDataframe(self, json):
        df = pd.DataFrame(json)
        df.rename(columns={'date': 'Timestamp', 'close': 'Close'}, inplace=True)
        df.set_index("Timestamp", inplace=True)
        df.index = df.index * 1000000000
        df.index = pd.to_datetime(df.index)
        return df


