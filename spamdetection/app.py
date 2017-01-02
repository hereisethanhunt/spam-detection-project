from __future__ import print_function
import httplib2
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import json
import base64
from flask import jsonify
import email
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os, random
import nltk
from nltk import word_tokenize, WordNetLemmatizer
from nltk.corpus import stopwords
import train as sf

from apiclient import errors
import shutil
from flask import Flask , render_template,url_for,redirect,request,flash,session
import json
import subprocess

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

htmlemail="htmlemail"
textemail="textemail"
dirtohtml="htmlemail/htmlemail"
dirtotext="textemail/textemail"
txt=".txt"
html=".html"
datasetemail=[]
textfile_list=[]

app = Flask(__name__)
app.secret_key = 'hereisethanhunt'


def get_credentials():
    

    store = oauth2client.file.Storage('credent.data')
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: 
            credentials = tools.run(flow, store)
        #print('Storing credentials to ' + credential_path)
    return credentials

filecontent=[]

foldert="textemail/"
folderh="htmlemail/"


def run_online(classifier, setting):
	ham_spam=[]
	for i in range(len(textfile_list)):
		features = sf.get_features(textfile_list[i], setting)
		if (len(features) == 0):
			break
		ham_spam.append(classifier.classify(features))
	return ham_spam

 
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


@app.route('/')
def index():
	return render_template('index.html')

@app.route('/authenticate')
def authenticate():
	hello= str(request.args.get('echo'))
	print (hello)
	newpatht = '/home/vishal/Desktop/spamdetection/textemail' 
	if not os.path.exists(newpatht):
		os.makedirs(newpatht)
	else:
		filelist = [ f for f in os.listdir(newpatht+"/") if f.endswith(".txt") ]
		#print (filelist)
		for f in filelist:
			os.remove(newpatht+"/"+f)

	newpathh = '/home/vishal/Desktop/spamdetection/htmlemail'
	if not os.path.exists(newpathh):
		os.makedirs(newpathh)
	else:
		filelist = [ f for f in os.listdir(newpathh+"/") if f.endswith(".txt") ]
		#print (filelist)
		for f in filelist:
			os.remove(newpathh+"/"+f)


	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	service = discovery.build('gmail', 'v1', http=http)
	
	try:
		response = service.users().messages().list(userId='me',q='%').execute()
		messages = []
		if 'messages' in response:
			messages.extend(response['messages'])

		while 'nextPageToken' in response:
			page_token = response['nextPageToken']
			response = service.users().messages().list(userId='me', q='%',pageToken=page_token).execute()
			messages.extend(response['messages'])

		with open('messageIDs.txt', 'w') as outfile:
			json.dump(messages, outfile)

	except errors.HttpError, error:
		print ("An error occurred:")
		print (error)


	for ids in range(0,40):
		message = service.users().messages().get(userId='me', id=messages[ids]['id']).execute()
		try:
			msg_str = base64.urlsafe_b64decode(message['payload']['parts'][1]['body']['data'].encode('ASCII'))
			mime_msg = email.message_from_string(msg_str)
			f=open(htmlemail+`ids`+html,"w")
			f.write(str(mime_msg))
			msg_str = base64.urlsafe_b64decode(message['payload']['parts'][0]['body']['data'].encode('ASCII'))
			mime_msg = email.message_from_string(msg_str)
			datasetemail.append(str(mime_msg))
			f1=open(textemail+`ids`+txt,"w")
			f1.write(str(mime_msg))
			os.rename(textemail+`ids`+txt, dirtotext+`ids`+txt)
			os.rename(htmlemail+`ids`+html, dirtohtml+`ids`+html)
			f.close()
			f1.close()
		except:
			continue

	print (datasetemail)
	return "hello"


@app.route('/displayit')
def displayit():
	file_list = os.listdir(folderh)
	file_list.sort()
	htmlfile_list=[]
	for a_file in file_list:
		f = open(folderh + a_file, 'r')
		htmlfile_list.append(f.read())
	f.close()
	newerlist = [[] for x in xrange(len(htmlfile_list))]
	print (len(htmlfile_list))
	for i in range(len(htmlfile_list)):
		newerlist[i].append(htmlfile_list[i]);

	print (newerlist)
	return jsonify(results=htmlfile_list)



@app.route('/display')
def display():
	file_list = os.listdir(foldert)
	file_list.sort()
	for a_file in file_list:
		f = open(foldert + a_file, 'r')
		textfile_list.append(f.read())
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
	hamspamarray=run_online(classifier, "")
	#detect_spam('dataset/ham/', classifier, "")
	
	#print('\nHAM:')
	#print_stat('dataset/ham/', classifier, "")
	#print('SPAM:')
	#print_stat('dataset/spam/', classifier, "")
	#explore_feats(spam)
	return jsonify(results=hamspamarray)

if __name__ == '__main__':
	app.run(debug = True)
