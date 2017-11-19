import pandas as pd
import pdb
import json
from cnnClassification import cnnClassification
from cnnPrediction import cnnPrediction
from evidenceSentencesToSummary import evidenceSentencesToSummary
from createSentenceDB import filterSentenceLength, setSentenceLength
from nltk.tokenize import sent_tokenize
from lda import ClassificationModel, Preprocessor



def sentenceToDocClassification():

    analyze = 0
    preprocessing = 1
    balanceData = 1
    validation = 1
    splitValidationDataInSentences = 0

    configFile = 'dataConfig.json'
    config_name = 'ICAAD_DV_sentences'
    #config_name = 'ICAAD_SA_sentences'
    #config_name = 'Manifesto_Minorities'


    with open(configFile) as data_file:
        sentences_config = json.load(data_file)[config_name]

    sentences = pd.read_csv(sentences_config['data_path'], encoding ='utf8')


    if balanceData:
        posSample = sentences[sentences[sentences_config['TARGET']]==sentences_config['categoryOfInterest']]
        negSample = sentences[sentences[sentences_config['TARGET']] == sentences_config['negCategory']].sample(len(posSample))
        sentences = pd.concat([posSample, negSample])

    if preprocessing:
        preprocessor = Preprocessor()
        sentences.text = sentences.text.apply(preprocessor.cleanText)


    sentenceClassifier = ClassificationModel(target=sentences_config['TARGET'], labelOfInterest=sentences_config['categoryOfInterest'])
    sentenceClassifier.data = sentences
    sentenceClassifier.createTarget()

    sentenceClassifier.setDataConfig(sentences_config)
    sentenceClassifier.validation = 1

    sentenceClassifier.splitDataset(random_state=10)


    if analyze:
        coi = sentenceClassifier.sentences[sentenceClassifier.sentences[sentences_config['TARGET']]==sentences_config['categoryOfInterest']]
        document_lengths = [len(word_tokenize(sentence)) for sentence in coi.text]
        plotter = ImagePlotter(True)
        #figure_path = path=os.path.join(PATH, sentences_config['DATASET'], 'figures', data_config['ID'] + '_evidenceSentences' + '.png')

        bins = range(1,100)
        plotter.plotHistogram(document_lengths, log=False, title= sentences_config['ID'] + ' frequency of evidence sentences length', xlabel='sentence length', ylabel='frequency', bins=bins, path=None)
        print 'max: ' + str(max(document_lengths))
        print 'min: ' + str(min(document_lengths))
        print 'median: ' + str(np.median(document_lengths))

    sentenceClassifier.max_document_length = max([len(x.split(" ")) for x in sentenceClassifier.trainData.text])
    print 'Maximal sentence length ' + str(sentenceClassifier.max_document_length)


    cnnClassification(sentenceClassifier, ITERATIONS=30, BATCH_SIZE=64)

    sentences_filename = '../data/' + sentences_config['DATASET'] + '/' + sentences_config['ID'] + '_sentencesValidationData.csv'


    if splitValidationDataInSentences:

        print 'Split Validation Data In Setences'
        data = pd.read_pickle('../data/ICAAD/ICAAD.pkl')
        validationIndices = sentenceClassifier.validationData.docID.unique()
        data = data[data.id.isin(validationIndices)]

        def splitInSentences(row):
            sentences = sent_tokenize(row.text)
            return [(row.id, row[data_config['label']], sentence) for sentence in sentences]

        sentenceDB = data.apply(splitInSentences, axis=1)
        sentenceDB = sum(sentenceDB.tolist(), [])
        sentenceDB = pd.DataFrame(sentenceDB, columns=['docID', data_config['label'], 'text'])

        sentenceDB['sentenceLength'] = sentenceDB.text.map(setSentenceLength)
        sentenceDB = sentenceDB[sentenceDB.sentenceLength.map(filterSentenceLength)]

        sentenceDB['text'] = sentenceDB['text'].str.lower()
        sentenceDB.to_csv(sentences_filename)

    else:

        sentenceDB = pd.read_csv(sentences_filename)


    predictedData = cnnPrediction(sentenceDB, sentences_config['label'], sentenceClassifier.output_dir)

    summaries = evidenceSentencesToSummary(predictedData, sentences_config['label'])


    summary_config_name = 'ICAAD_DV_summaries'
    with open(configFile) as data_file:
        summary_config = json.load(data_file)[summary_config_name]


    if preprocessing:
        preprocessor = Preprocessor()
        summaries.text = summaries.text.apply(preprocessor.cleanText)

    docClassifier = ClassificationModel(target=summary_config['TARGET'], labelOfInterest=summary_config['categoryOfInterest'])
    docClassifier.data = summaries
    docClassifier.validation = 0
    docClassifier.createTarget()

    docClassifier.setDataConfig(summary_config)
    docClassifier.splitDataset(random_state=10)


    docClassifier.max_document_length = max([len(x.split(" ")) for x in docClassifier.trainData.text])
    print 'Maximal sentence length ' + str(sentenceClassifier.max_document_length)


    cnnClassification(docClassifier, BATCH_SIZE=32, ITERATIONS=30)

    pdb.set_trace()




if __name__=='__main__':
    sentenceToDocClassification()