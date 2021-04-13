from nltk.corpus import stopwords
import matplotlib.pyplot as plt
from DataProcessing.NewsLoader import NewsLoader
import tensorflow as tf
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
from datetime import datetime

class LSTM:

    model = None

    #parameters
    vocab_size = None
    embedding_dim = None
    max_length = None
    trunc_type = None
    padding_type = None
    oov_tok = None
    training_portion = None

    train_padded = None
    training_label_seq = None

    validation_padded = None
    validation_label_seq = None

    labels = ['none','pos', 'neg']



    STOPWORDS = set(stopwords.words('english'))

    def __init__(self, vocab_size = 2000,embedding_dim = 64,max_length = 118,trunc_type = 'post',padding_type = 'post',
                 oov_tok = '<OOV>',training_portion = .8,train_padded=None,training_label_seq=None,validation_padded=None,validation_label_seq=None):
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.max_length = max_length
        self.trunc_type = trunc_type
        self.padding_type = padding_type
        self.oov_tok = oov_tok
        self.training_portion = training_portion
        self.train_padded = train_padded
        self.training_label_seq = training_label_seq
        self.validation_padded = validation_padded
        self.validation_label_seq = validation_label_seq

    #Loading and preprocessing data for the model
    def loadXPrepData(self,config):

        newsLoader = NewsLoader(config=config,filename="")
        newsLoader.fetchAndLoadNewsLabeled(url="")

        train_titles,train_labels,validation_titles,validation_labels = newsLoader.splittingDataTrainTest(.8)
        #print(len(train_titles))

        word_index = newsLoader.titlesTokenizer(self.vocab_size,self.oov_tok,train_titles)

        self.train_padded,self.validation_padded=newsLoader.Padding(train_titles,self.padding_type,self.trunc_type,validation_titles)

        self.training_label_seq,self.validation_label_seq=newsLoader.labelsTokenizer(train_labels,validation_labels)

        reverse_word_index = dict([(value, key) for (key, value) in word_index.items()])

        #check if its working
        def decode_article(text):
            return ' '.join([reverse_word_index.get(i, '?') for i in text])
        print(decode_article(self.train_padded[10]))
        print('---')
        print(train_titles[10])


    def build(self):

        #self.model = instance.build(columns)
        model = tf.keras.Sequential([
            # Add an Embedding layer expecting input vocab of size 5000, and output embedding dimension of size 64 we set at the top
            tf.keras.layers.Embedding(self.vocab_size, self.embedding_dim),
            tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(self.embedding_dim)),
            #    tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(32)),
            # use ReLU in place of tanh function since they are very good alternatives of each other.
            tf.keras.layers.Dense(self.embedding_dim, activation='relu'),
            # Add a Dense layer with 6 units and softmax activation.
            # When we have multiple outputs, softmax convert outputs layers into a probability distribution.
            tf.keras.layers.Dense(3, activation='softmax')
        ])
        model.summary()
        self.model = model

        return self

    def train(self,num_epochs):

        self.model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        history = self.model.fit(self.train_padded, self.training_label_seq, epochs=num_epochs, validation_data=(self.validation_padded, self.validation_label_seq), verbose=2)
        self.model.train
        return history


    def plot_graphs(self,history, string):
        plt.plot(history.history[string])
        plt.plot(history.history['val_' + string])
        plt.xlabel("Epochs")
        plt.ylabel(string)
        plt.legend([string, 'val_' + string])
        plt.show()

    def predict(self,input,tokenizer):

        seq = tokenizer.texts_to_sequences(input)
        print(seq)
        print(self.max_length)
        padded = pad_sequences(seq, maxlen=self.max_length)
        pred = self.model.predict(padded)
        labels = ['none','pos','neg']
        print(pred)
        print(np.argmax(pred))
        print("Predicted output:")
        print(pred, labels[np.argmax(pred)])


    def saveModelToFile(self, model_code, timestamp=None):
        # serialize model to JSON
        model_json = self.model.to_json()

        if timestamp is None:
            timestamp = datetime.timestamp(datetime.now())

        with open("SavedModels/Sentiment/" + model_code + "-" + str(timestamp) + ".json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        self.model.save_weights("SavedModels/Sentiment/" + model_code + "-" + str(timestamp) + ".tf")
        print("Saved model to disk")

    def batch(data, n=1):
        #grouping data by n. If its 12 means that 12 samples of data are batched toghether.
        for g, df in data.groupby(np.arange(len(data)) // n):
            yield df

    def saveModelWeights(self):
        #under construction
        return self