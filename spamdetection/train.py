from __future__ import print_function, division
import nltk
import os
import random
from collections import Counter
from nltk import word_tokenize, WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk import NaiveBayesClassifier, classify

stoplist = stopwords.words('english')

def init_lists(folder):
    a_list = []
    file_list = os.listdir(folder)
    for a_file in file_list:
        f = open(folder + a_file, 'r')
        a_list.append(f.read())
    f.close()
    return a_list

def preprocess(sentence):
    port = SnowballStemmer("english")
    sentence1 = (" ".join([port.stem(word1.lower()) for word1 in word_tokenize(unicode(sentence, errors='ignore'))])).encode("utf-8")
    #print (sentence1)
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(word) for word in word_tokenize(unicode(sentence1, errors='ignore'))]

def get_features(text, setting):
    if setting=='bow':
        return {word: count for word, count in Counter(preprocess(text)).items() if not word in stoplist}
    else:
        return {word: True for word in preprocess(text) if not word in stoplist}
 
def train(features, samples_proportion):
    train_size = int(len(features) * samples_proportion)
    train_set, test_set = features[:train_size], features[train_size:]
    print ('Training set size = ' + str(len(train_set)) + ' emails')
    print ('Test set size = ' + str(len(test_set)) + ' emails')
    classifier = NaiveBayesClassifier.train(train_set)
    return train_set, test_set, classifier
 
def evaluate(train_set, test_set, classifier):
    print ('Accuracy on the training set = ' + str(classify.accuracy(classifier, train_set)))
    print ('Accuracy of the test set = ' + str(classify.accuracy(classifier, test_set)))
    #classifier.show_most_informative_features(20)
 
if __name__ == "__main__":
    spam = init_lists('dataset/spam/')
    ham = init_lists('dataset/ham/')
    all_emails = [(email, 'spam') for email in spam]
    all_emails += [(email, 'ham') for email in ham]
    random.shuffle(all_emails)
    print ('Corpus size = ' + str(len(all_emails)) + ' emails')
    # f=open("datawithlabel.txt","w")
    # for x in all_emails:
    # 	f.write(x[0])
    # 	f.write("\n")
    # 	f.write(x[1])
    # 	f.write("\n")  
    #print (all_emails) #ham because of shuffling
 
    all_features = [(get_features(email, 'bow'), label) for (email, label) in all_emails]
    print ('Collected ' + str(len(all_features)) + ' feature sets')
    #print (all_features)
 

    train_set, test_set, classifier = train(all_features, 0.7)
 
    evaluate(train_set, test_set, classifier)
