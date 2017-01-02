from __future__ import print_function, division
import os, random
import nltk
import glob
from nltk import word_tokenize, WordNetLemmatizer
from nltk.corpus import stopwords
import train as sf

filecontent=[]

foldert="new-emails/textemail/"
folderh="new-emails/htmlemail/"
htmlfile_list = []
textfile_list = []
ham_spam=[]
def run_online(classifier, setting):
    for i in range(len(textfile_list)):
        features = sf.get_features(textfile_list[i], setting)
        if (len(features) == 0):
            break
        print (textfile_list[i])
        # print (htmlfile_list[i])
        print (classifier.classify(features))
        ham_spam.append(classifier.classify(features))

 
def detect_spam(folder, classifier, setting):
    output = {}
    file_list = os.listdir(folder)
    for a_file in file_list:
        f = open(folder + a_file, 'r')
        features = sf.get_features(f.read(), setting)
        f.close()
        output[a_file] = classifier.classify(features)
    for item in output.keys():
        print (item + '\t' + output.get(item))
 
def print_stat(folder, classifier, setting):
    total = 0
    spam = 0
    ham = 0
    file_list = os.listdir(folder)
    for a_file in file_list:
        total+=1
        f = open(folder + a_file, 'r')
        features = sf.get_features(f.read(), setting)
        f.close()
        if classifier.classify(features) == 'spam':
            spam+=1
        else:
            ham+=1
    print('%.2f' % (100*float(spam)/float(total)) + '% spam emails')
    print('%.2f' % (100*float(ham)/float(total)) + '% ham emails')
 
# def explore_feats(dataset):
#     stoplist = stopwords.words('english')
#     lemmatizer = WordNetLemmatizer()
#     words = []
#     for email in dataset:
#         words += [lemmatizer.lemmatize(word.lower()) for word in
#         word_tokenize(unicode(email, errors='ignore')) if not word.lower() in stoplist]
#     fdist = nltk.FreqDist(words)
#     fdist.plot(75, cumulative=True)
 
if __name__ == "__main__":

    file_list = os.listdir(foldert)
    file_list.sort()
    for a_file in file_list:
        f = open(foldert + a_file, 'r')
        textfile_list.append(f.read())
    f.close()
    
    
    file_list = os.listdir(folderh)
    file_list.sort()
    for a_file in file_list:
        f = open(folderh + a_file, 'r')
        htmlfile_list.append(f.read())
    f.close()


    spam = sf.init_lists('dataset/spam/')
    ham = sf.init_lists('dataset/ham/')
    all_emails = [(email, 'spam') for email in spam]
    all_emails += [(email, 'ham') for email in ham]
 

    random.shuffle(all_emails)
    print ('Corpus size = ' + str(len(all_emails)) + ' emails')
 
    all_features = [(sf.get_features(email, ''), label) for (email, label) in all_emails]
    
    train_set, test_set, classifier = sf.train(all_features, 0.8)
    
    sf.evaluate(train_set, test_set, classifier)
    
    #classify your new email
    run_online(classifier, "")
 
    #detect_spam('dataset/ham/', classifier, "")
 
    print('\nHAM:')
    print_stat('dataset/ham/', classifier, "")
    print('SPAM:')
    print_stat('dataset/spam/', classifier, "")
    #explore_feats(spam)