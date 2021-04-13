import json

import pandas
from DataProcessing.Preprocessor import Preprocessor

from DataProcessing.PoloniexDataLoader import PoloniexDataLoader
from DataProcessing.NewsLoader import NewsLoader
from Models.NN.SentimentClassifier.LSTM import LSTM

CONFIG_FILE = 'etc/config.json'
with open(CONFIG_FILE) as config:
    CONFIG = json.load(config)

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':


    url = ""
    currency_pair = "USDT_BTC"
    if CONFIG["poloniex_url"] is not None:
        print("Poloniex data retrieval...")
        poloniexDataLoader = PoloniexDataLoader(config=CONFIG,filename=currency_pair)
        df = poloniexDataLoader.fetchHistoricalData(CONFIG["poloniex_url"], currency_pair, start_timestamp=1586630384, end_timestamp=1615131712,period=86400)


        #csvSanitizer = DataSanitizer.CsvSanitizer("data/price/poloniex-" + currency_pair + "-price.csv")
        poloniexDataLoader.write(df, add_sanitization_suffix=False,csv_filename=currency_pair)
        #print(df)
    else:
        print("URL in etc/CONFIG is not set correctly")
        exit(1)

    csv_filename = 'data/price/USDT_BTC.csv'

    preprocessor = Preprocessor()

    data = Preprocessor.load_dataset(csv_filename)

    data.drop(['high','low','open','volume','quoteVolume','weightedAverage'],inplace=True,axis=1)

    isCurrentMax = preprocessor.calculateIsMaxColumn(data, 'Close', 12)

    data["isCurrentMax"] = isCurrentMax

    isCurrentMin = preprocessor.calculateIsMinColumn(data, 'Close', 12)

    data["isCurrentMin"] = isCurrentMin

    data = preprocessor.assignClassByStrategy(data,"BuyLowSellHigh")

    print(len(data))
    print(data)

    preprocessor.write(data,csv_filename='BuyLowSellHigh')
    exit(1)

    vocab_size = 2000
    oov_tok = '<OOV>'
    padding_type = 'post'
    trunc_type = 'post'

    embedding_dim = 64
    training_portion=.8
    num_epochs = 2


    #data load and prepare
    newsLoader = NewsLoader(config=CONFIG,filename="")
    newsLoader.fetchAndLoadNewsLabeled(url="")

    train_titles,train_labels,validation_titles,validation_labels = newsLoader.splittingDataTrainTest(.8)
    #print(len(train_titles))

    word_index = newsLoader.titlesTokenizer(vocab_size,oov_tok,train_titles)

    train_padded,validation_padded=newsLoader.Padding(train_titles,padding_type,trunc_type,validation_titles)

    training_label_seq,validation_label_seq=newsLoader.labelsTokenizer(train_labels,validation_labels)

    reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

    #check if its working
    def decode_article(text):
        return ' '.join([reverse_word_index.get(i, '?') for i in text])
    print(decode_article(train_padded[10]))
    print('---')
    print(train_titles[10])

    #build, train and test model predictions

    lstmModel = LSTM(vocab_size,embedding_dim,newsLoader.max_length,trunc_type,padding_type,oov_tok,training_portion,train_padded,training_label_seq,validation_padded,validation_label_seq)

    lstmModel.build()
    history = lstmModel.train(num_epochs)

    lstmModel.plot_graphs(history, "accuracy")
    lstmModel.plot_graphs(history, "loss")



    txt = ["Newsflash Bitcoin Price Hits Day High is Next"]
    lstmModel.predict(txt,newsLoader.tokenizer)
    #lstmModel.saveModelToFile("LSTM")


    exit(1)

    url = ""
    currency_pair = "USDT_BTC"
    if CONFIG["poloniex_url"] is not None:
        print("Poloniex data retrieval...")
        poloniexDataLoader = PoloniexDataLoader(config=CONFIG,filename=currency_pair)
        df = poloniexDataLoader.fetchHistoricalData(CONFIG["poloniex_url"], currency_pair, start_timestamp=1612712512, end_timestamp=1615131712,period=86400)


        #csvSanitizer = DataSanitizer.CsvSanitizer("data/price/poloniex-" + currency_pair + "-price.csv")
        poloniexDataLoader.write(df, add_sanitization_suffix=False,csv_filename=currency_pair)
        print(df)
    else:
        print("URL in etc/CONFIG is not set correctly")
        exit(1)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
