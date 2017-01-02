from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import json
import base64
import email
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import os

from apiclient import errors

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


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

def main():
    
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

    
    htmlemail="htmlemail"
    textemail="textemail"
    dirtohtml="htmlemail/htmlemail"
    dirtotext="textemail/textemail"
    txt=".txt"
    html=".html"
    datasetemail=[]
    for ids in range(0,20):
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
        #print (message)
        
        
        #print (messages[ids]['id'])

    #print (str(message))
    # f = open("messages.txt","w")
    # f.write(str(message))
        

    
    # with open('messages.txt', 'r') as handle:
    #     parsed = json.load(handle)
    #     f.write(json.dumps(parsed, indent=4, sort_keys=True))
    # f.close()
    # f = open("test.json","r")
    #d = json.load(f)
    # f = open("test.json","w")
    # for x in message:
    #     parsed = json.load(str(x))
    #     f.write(json.dumps(parsed, indent=4, sort_keys=True))
    # f.close()
    #vari = message['payload']['parts'][0]['body']['data']

    #print (base64.b64decode((message['payload']['parts'][0]['body']['data']) + "========"))
    
    

    
    #print (mime_msg)






    #with open('messages.json', 'w') as outfile:

        #json.dump(message, outfile)
        # data=json.loads(outfile)
        

if __name__ == '__main__':
    main()