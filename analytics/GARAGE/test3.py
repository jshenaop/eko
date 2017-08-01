import collections
import nltk.classify.util, nltk.metrics
from nltk.classify import NaiveBayesClassifier, MaxentClassifier, SklearnClassifier
import csv
from sklearn import cross_validation
from sklearn.svm import LinearSVC, SVC
import random
from nltk.corpus import stopwords
import itertools
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures

posdata = []
with open('positive-data.csv', 'rb') as myfile:
    reader = csv.reader(myfile, delimiter=',')
    for val in reader:
        posdata.append(val[0])

negdata = []
with open('negative-data.csv', 'rb') as myfile:
    reader = csv.reader(myfile, delimiter=',')
    for val in reader:
        negdata.append(val[0])


def word_split(data):
    data_new = []
    for word in data:
        word_filter = [i.lower() for i in word.split()]
        data_new.append(word_filter)
    return data_new


def word_split_sentiment(data):
    data_new = []
    for (word, sentiment) in data:
        word_filter = [i.lower() for i in word.split()]
        data_new.append((word_filter, sentiment))
    return data_new


def word_feats(words):
    return dict([(word, True) for word in words])


stopset = set(stopwords.words('english')) - set(('over', 'under', 'below', 'more', 'most', 'no', 'not', 'only', 'such',
                                                 'few', 'so', 'too', 'very', 'just', 'any', 'once'))


def stopword_filtered_word_feats(words):
    return dict([(word, True) for word in words if word not in stopset])


def bigram_word_feats(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    """
    print words
    for ngram in itertools.chain(words, bigrams): 
        if ngram not in stopset: 
            print ngram
    exit()
    """
    return dict([(ngram, True) for ngram in itertools.chain(words, bigrams)])


def bigram_word_feats_stopwords(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigrams = bigram_finder.nbest(score_fn, n)
    """
    print words
    for ngram in itertools.chain(words, bigrams): 
        if ngram not in stopset: 
            print ngram
    exit()
    """
    return dict([(ngram, True) for ngram in itertools.chain(words, bigrams) if ngram not in stopset])


# Calculating Precision, Recall & F-measure
def evaluate_classifier(featx):
    negfeats = [(featx(f), 'neg') for f in word_split(negdata)]
    posfeats = [(featx(f), 'pos') for f in word_split(posdata)]

    negcutoff = len(negfeats) * 3 / 4
    poscutoff = len(posfeats) * 3 / 4

    trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
    testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]

    # using 3 classifiers
    classifier_list = ['nb', 'maxent', 'svm']

    for cl in classifier_list:
        if cl == 'maxent':
            classifierName = 'Maximum Entropy'
            classifier = MaxentClassifier.train(trainfeats, 'GIS', trace=0, encoding=None, labels=None, sparse=True,
                                                gaussian_prior_sigma=0, max_iter=1)
        elif cl == 'svm':
            classifierName = 'SVM'
            classifier = SklearnClassifier(LinearSVC(), sparse=False)
            classifier.train(trainfeats)
        else:
            classifierName = 'Naive Bayes'
            print(trainfeats)
            classifier = NaiveBayesClassifier.train(trainfeats)

        refsets = collections.defaultdict(set)
        testsets = collections.defaultdict(set)

        for i, (feats, label) in enumerate(testfeats):
            refsets[label].add(i)
            observed = classifier.classify(feats)
            testsets[observed].add(i)

        accuracy = nltk.classify.util.accuracy(classifier, testfeats)


evaluate_classifier(word_feats)
# evaluate_classifier(stopword_filtered_word_feats)
# evaluate_classifier(bigram_word_feats)
# evaluate_classifier(bigram_word_feats_stopwords)