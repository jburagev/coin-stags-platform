import psycopg2 as psycopg2
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
from poloniex import Poloniex
import requests
import pandas as pd
import os
#import mysql.connector

class NewsLoader:

    csv_filename = ''
    conn = None
    labels=[]
    titles=[]
    tokenizer=None
    max_length=None


    def __init__(self, config,filename):
        self.csv_filename = filename
        print(config["DB_DATABASE"])
        #self.conn = mysql.connector.connect(user=config["DB_USERNAME"], password=config["DB_PASSWORD"],
        #                              host=config["DB_HOST"],
        #                              database=config["DB_DATABASE"])
        self.conn = psycopg2.connect(
            dbname=config["DB_DATABASE"], user=config["DB_USERNAME"], password=config["DB_PASSWORD"], host=config["DB_HOST"], port=config["DB_PORT"]
        )



    def fetchAndLoadNewsLabeled(self, url, currency_pair='BTC', start_timestamp=1439013600, end_timestamp=None,
                            period=86400, resolution='auto'):

        cur = self.conn.cursor()

        cur.execute('SELECT cryptopanic_slug,cryptopanic_item_published_at,sentiment_weight FROM news_source_sentiment_analysis WHERE sentiment_weight IS NOT NULL AND cryptopanic_item_published_at > \'11/12/2018\' ORDER BY cryptopanic_item_published_at ASC')

        print("Number of labeled news: ", cur.rowcount)

        row = cur.fetchone()

        while row is not None:
            #print(row)
            if row[2] == 1:
                self.labels.append("pos")
            else:
                self.labels.append("neg")

            #if row[2] == 0:
            #    self.labels.append("none")

            self.titles.append(row[0])
            row = cur.fetchone()

        return self.labels,self.titles


    def splittingDataTrainTest(self,training_portion):

        train_size = int(len(self.titles) * training_portion)

        train_titles = self.titles[0: train_size]
        train_labels = self.labels[0: train_size]

        validation_titles = self.titles[train_size:]
        validation_labels = self.labels[train_size:]

        return train_titles,train_labels,validation_titles,validation_labels

    def titlesTokenizer(self,vocab_size,oov_tok,train_titles):

        self.tokenizer = Tokenizer(num_words = vocab_size, oov_token=oov_tok)
        self.tokenizer.fit_on_texts(train_titles)
        word_index = self.tokenizer.word_index
        dict(list(word_index.items())[0:10])

        return word_index

    def Padding(self,train_titles,padding_type,trunc_type,validation_titles):


        train_sequences = self.tokenizer.texts_to_sequences(train_titles)
        #print(train_sequences[10])

        self.max_length = self.longestTextInArray(train_titles)

        train_padded = pad_sequences(train_sequences, maxlen=self.max_length, padding=padding_type, truncating=trunc_type)
        #print(self.longestTextInArray(train_titles))
        #print(len(train_sequences[1]))
        #print(train_titles[1])
        #print(len(train_padded[0]))

        #print(len(train_sequences[1]))
        #print(len(train_padded[1]))

        #print(len(train_sequences[10]))
        #print(len(train_padded[10]))

        validation_sequences = self.tokenizer.texts_to_sequences(validation_titles)
        validation_padded = pad_sequences(validation_sequences, maxlen=self.max_length, padding=padding_type, truncating=trunc_type)

        #print(len(validation_sequences))
        #print(validation_padded.shape)

        return train_padded,validation_padded

    def labelsTokenizer(self,train_labels,validation_labels):

        label_tokenizer = Tokenizer()
        label_tokenizer.fit_on_texts(self.labels)

        training_label_seq = np.array(label_tokenizer.texts_to_sequences(train_labels))
        validation_label_seq = np.array(label_tokenizer.texts_to_sequences(validation_labels))
        '''
        print(training_label_seq[0])
        print(training_label_seq[1])
        print(training_label_seq[2])
        print(training_label_seq.shape)

        print(validation_label_seq[0])
        print(validation_label_seq[1])
        print(validation_label_seq[2])
        print(validation_label_seq.shape)
        '''
        return training_label_seq,validation_label_seq


    def longestTextInArray(self,array):
        #check the longes text by counting the words
        max_len = max([len(i) for i in array])

        return max_len