from __future__ import print_function

import httplib2
import os
import json
import base64
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import AccessTokenCredentials, OAuth2Credentials

from apiclient.discovery import build



def build_service(credentials):
  http = httplib2.Http()
  #credentials.refresh(http) # may be needed
  http = credentials.authorize(http)
  return build('gmail', 'v1', http=http)


def get_labels(s):
    labels = s.users().labels().list(userId='me').execute().get('labels')
    results = []
    for l in labels:
        results.append(l)
    
    return results
    

def get_label_id_from_name(s, name):
    found = [ o['id'] for o in get_labels(s) if o['name'] == name ]
    if len(found) == 1:
        return found[0]
    else:
        raise Exception("Could not find label with name: " + name)


def get_message_ids(service, label_id):
    result = service.users().messages().list(userId='me', labelIds=label_id).execute()
    msgs = result.get('messages', [])
    return [o['id'] for o in msgs]


def get_thread_ids(service, label_id, pageToken='', maxResults=1000):
    result = service.users().threads().list(userId='me', labelIds=label_id, pageToken=pageToken, maxResults=maxResults).execute()
    msgs = result.get('threads', [])
    nextPageToken = result.get('nextPageToken')

    ids = [o['id'] for o in msgs]
    return (ids, nextPageToken)


def get_messages(service, label_id):
    msgs = get_message_ids(service, label_id)

    result = []
    for m in msgs:
        o = service.users().messages().get(userId='me', id=m['id']).execute()
        return_msg = {'subject': 'NO_SUBJECT', 'body': 'NO_BODY', 'id': o['id']} 

        try:
            print(o)
            payload = o['payload']
            subject = [x['value'] for x in o['payload']['headers'] if x['name'] == 'Subject']


            if len(subject) > 0:
                print("-------------------------")
                print("Subject: " + subject[0])
                print("-------------------------")
                return_msg['subject'] = subject[0]
        
                if payload['body']['size'] > 0:
                    print("Body")
                    decoded = base64.b64decode(payload['body']['data'])
                    return_msg['body'] = decoded
                    #print(decoded)
                        

                for p in payload['parts']:
                    print("Parts")
                    if p['mimeType'] == 'text/plain':
                        decoded = base64.b64decode(p['body']['data'])
                        return_msg['body'] = decoded
                        #print(decoded)

                #print("Object")
                #print(o)
                print()
                print()
                
                #print(m['payload']['body'])
        except Exception as e:
            print("error")
            print(e)

        result.append(return_msg)

    return result


def trash_thread(service, id):
    service.users().threads().trash(userId='me', id=id).execute()

def delete_thread(service, id):
    service.users().threads().delete(userId='me', id=id).execute()

# read credentials
credential_file = 'credentials.json'
credential_text = open(credential_file).read()
credentials = OAuth2Credentials.from_json(credential_text)
#print(credentials)


service = build_service(credentials)

label_name = sys.argv[1]
mode = sys.argv[2] # delete, trash, dryrun
label_id = get_label_id_from_name(service, label_name)


processed = 0
page_limit = 500
total_limit = 5000
pageToken = ''
errors = 0

while (True):
    (thread_ids, pageToken) = get_thread_ids(service, label_id, pageToken, page_limit)
    
    print("Found " + str(len(thread_ids)) + " threads under the label: " + label_name)
    #raw_input("Press enter to trash all.")

    for thread_id in thread_ids:
        try:
            processed = processed + 1

            if mode == 'trash':
                print(str(processed) + ". Trashing..." + str(thread_id))
                trash_thread(service, thread_id)
            elif mode == 'delete':
                print(str(processed) + ". Deleting..." + str(thread_id))
                delete_thread(service, thread_id)
            else:
                print(str(processed) + ". Dry run..." + str(thread_id))


        except Exception as e:
            errors = errors + 1
            print("Error for thread: " + thread_id)
            print(e)

    if processed >= total_limit:
        break

    if pageToken is None: 
        break



print("COMPLETED! Processed " + str(processed) + " messages");
if errors > 0:
    print("Errors: " + str(errors))




#msgs = get_messages(service)
#
#print('####################')
#print("Printing messages!")
#
#ids = []
#for m in msgs:
#    print(m['id'])
#    print(m['subject'])
#    print(m['body'])
#    print('------------------')
#    print()
#    ids.append(m['id'])
