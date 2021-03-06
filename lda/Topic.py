import listUtils as utils
from ImagePlotter import ImagePlotter 
import os
import pandas as pd

class Topic:

    def __init__(self):
        self.number = None
        self.wordDistribution = []
        self.relatedDocuments = []

    def addTopic(self, topicTuple):
        self.number = topicTuple[0]
        self.wordDistribution = topicTuple[1]

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def setAttribute(self, name, value):
        setattr(self, name, value)

    def getWords(self):
        return zip(*self.wordDistribution)[0][0:7]

    def labelTopic(self, word2vec, categories):
        topicWords = word2vec.filterList(self.getWords()) 
        similarWords = word2vec.getSimilarWords(topicWords)
        meanSimilarity = word2vec.getMeanSimilarity(categories, similarWords)
        self.keywords = pd.DataFrame(meanSimilarity, index=categories).sort_values(0, ascending=False)

    def findIntruder(self, word2vec):
       topicWords = word2vec.filterList(self.getWords())
       if not topicWords:
           self.intruder = 'default'
       else:
           self.intruder = word2vec.net.doesnt_match(topicWords)
    
    
    def computeSimilarityScore(self, word2vec):
        topicWords = word2vec.filterList(self.getWords())
        if not topicWords:
            self.pairwiseSimilarity = []
            self.medianSimilarity = 0
        else:
            similarityMatrix = [word2vec.wordToListSimilarity(word, topicWords) for word in topicWords]
            self.pairwiseSimilarity = utils.getUpperSymmetrixMatrix(similarityMatrix)
            self.medianSimilarity = utils.getMedian(self.pairwiseSimilarity)

    def getRelevanceHistogram(self, info):
        imageFolder = 'results/' + info.data + '_' + info.identifier + '/Images'
        self.createFolder(imageFolder)
        path = imageFolder + '/documentRelevance_topic%d.jpg' % self.number
        if zip(*self.relatedDocuments)!=[]:
            self.relevanceScores = zip(*self.relatedDocuments)[0]
        else:
            self.relevanceScores = [0]

        title = 'Frequency of Relevant Documents for Topic %d' % self.number
        plotter = ImagePlotter()
        plotter.plotHistogram(self.relevanceScores, title, path, 'Relevance', 'Number of Documents', log=1, open=0)

        
                
    def createFolder(self, path):
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise


