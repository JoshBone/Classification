from docLoader import loadData
from Preprocessor import Preprocessor
from FeatureExtractor import FeatureExtractor
import cPickle as pickle
import listUtils as utils
import pandas as pd
import numpy as np
import os
import pdb

class Collection:
    
    def __init__(self, path=None):
        self.data = pd.DataFrame() 
        if path:
            self.path = path
            self.data = loadData(path)
        self.nrDocs = len(self.data)


    def cleanDataframe(self, textField='text'):
        dataWithText = self.data[self.data[textField].notnull()]
        cleanDataframe = dataWithText.dropna(axis=1, how='all')
        self.data  = cleanDataframe.reset_index()
        self.nrDocs = len(self.data)


    def vectorize(self, vecType='tfidf', vocabulary=None):
        self.buildVectorizer(vecType=vecType, ngram_range=(1,2), min_df=5, max_df=0.50, max_features=8000, binary=False, vocabulary=vocabulary)
        self.trainVectorizer(vecType)


    def buildVectorizer(self, vecType='tfIdf', min_df=10, max_df=0.5, stop_words='english', ngram_range = (1,2), max_features=8000, vocabulary=None, binary=False):
        self.preprocessor = Preprocessor(processor=vecType, min_df=min_df, max_df=max_df, stop_words=stop_words, ngram_range=ngram_range, max_features=max_features, vocabulary=vocabulary, binary=binary)


    def trainVectorizer(self, vecType='tfIdf'):
        trainDocs = self.data.text.tolist()
        self.data[vecType] = self.preprocessor.trainVectorizer(trainDocs)
        self.vocabulary = self.preprocessor.vocabulary


    def save(self, path):
        self.savePreprocessor(path)
        with open(path +'.pkl', 'wb') as f:
            pickle.dump(self, f, -1)

    
    def load(self, path):
        collection = pickle.load(open(path+'.pkl', 'rb'))
        collection.loadPreprocessor(path)
        return collection


    def savePreprocessor(self, path):
        if hasattr(self, 'preprocessor'):
            self.preprocessor.save(path)
            del self.preprocessor


    def loadPreprocessor(self, path):
        preprocessor = Preprocessor()
        if os.path.exists(path+'.pkl'):
            self.preprocessor = preprocessor.load(path)
            self.vocabulary = self.preprocessor.vocabulary

    
    def existsProcessedData(self, path):
        return os.path.exists(path + '.pkl')

    
    def cleanTexts(self):
        preprocessor = Preprocessor()
        self.applyToRows('text', preprocessor.removeHTMLtags, 'cleanText')
        self.applyToRows('cleanText', preprocessor.cleanText, 'cleanText')
        self.applyToRows('cleanText', preprocessor.numbersInTextToDigits, 'cleanText')


    def extractEntities(self):
        featureExtractor = FeatureExtractor()
        self.applyToRows('text', featureExtractor.entities, 'entities')

    
    def applyToRows(self, field, fun, name, args=None):
        if args:
            self.data[name] = self.data.apply(lambda doc: fun(doc[field], args), axis=1)
        else:
            self.data[name] = self.data.apply(lambda doc: fun(doc[field]), axis=1)
