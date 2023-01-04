import json
import nltk
import joblib
import warnings
import random
import numpy as np
from nltk.stem.lancaster import LancasterStemmer

warnings.filterwarnings('ignore')


class ChatbotModel():
    def __init__(self):
        nltk.download('punkt')
        self.stemmer = LancasterStemmer()

        with open('./src/nlp/intents.json') as f:
            self.data = json.load(f)

        self.model = joblib.load('./src/nlp/models/chat_bot.pkl')
        self.words = joblib.load('./src/nlp/models/words.pkl')
        self.labels = joblib.load('./src/nlp/models/labels.pkl')

    def bag_of_words(self, s, words):
        bag = [0 for _ in range(len(words))]

        s_words = nltk.word_tokenize(s)
        s_words = [self.stemmer.stem(w.lower()) for w in s_words]

        for se in s_words:
            for i, w in enumerate(words):
                if w == se:
                    bag[i] = 1

        return bag

    def get_response(self, text_inp):
        res = 'I am sorry, I cannot answer that...'
        result = self.model.predict([self.bag_of_words(text_inp, self.words)])
        result_ind = np.argmax(result)
        tag = self.labels[result_ind]

        for tg in self.data['intents']:
            if tg['tag'] == tag:
                res = tg['responses']
        return random.choice(res)


if __name__ == "__main__":
    obj = ChatbotModel()
    while True:
        query = input("Enter: ")
        print(obj.get_response(query))
