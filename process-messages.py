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
from oauth2client.client import OAuth2Credentials

from apiclient.discovery import build
from apiclient.http import BatchHttpRequest


def get_http(creds):
  http = httplib2.Http()
  http = credentials.authorize(http)
  return http

def build_service(credentials):
  http = get_http(credentials)
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


def get_message_ids(service, query, pageToken='', maxResults=500):
    result = service.users().messages().list(userId='me', q=query, pageToken=pageToken, maxResults=maxResults).execute()
    msgs = result.get('messages', [])
    nextPageToken = result.get('nextPageToken')

    ids = [o['id'] for o in msgs]
    return (ids, nextPageToken)

def get_thread_ids(service, label_id, pageToken='', maxResults=500):
    result = service.users().threads().list(userId='me', labelIds=label_id, pageToken=pageToken, maxResults=maxResults).execute()
    msgs = result.get('threads', [])
    nextPageToken = result.get('nextPageToken')

    ids = [o['id'] for o in msgs]
    return (ids, nextPageToken)

def create_batch(callback):
    return service.new_batch_http_request(callback=callback)

def execute_batch(creds, batch):
    http = get_http(creds)
    return batch.execute(http=http)

def get_message(service, id):
    return service.users().messages().get(userId='me', id=id).execute()

def get_messages(service, label_id):
    msgs = get_message_ids(service, label_id)

    result = []
    for m in msgs:
        o = get_message(service, m)
     
        result.append(return_msg)

    return result

def trash_thread(service, id):
    service.users().threads().trash(userId='me', id=id).execute()

def delete_thread(service, id):
    service.users().threads().delete(userId='me', id=id).execute()

def get_all_messages(service, label, limit):
    pageToken = ''
    msgs = []

    def callback(i, r, e):
        if e is None:
            msgs.append(r)

    all_ids = []
    total = 0
    while (True):
        if pageToken is None or total >= limit:
            break

        (msg_ids, pageToken) = get_message_ids(service, label, pageToken)

        print("total..." + str(total))
        batch = create_batch(callback)
        for id in msg_ids:
            total = total + 1
            batch.add(service.users().messages().get(userId='me', id=id))

        print("executing batch...")
        execute_batch(credentials, batch)

    return msgs

def batch_delete_messages(service, ids):
        def callback(a,b,c):
            pass

        batch = create_batch(callback)
        for id in ids:
            batch.add(service.users().messages().delete(userId='me', id=id))

        print("executing batch...")
        execute_batch(credentials, batch)
    

def parse_message(o):
    return_msg = {'subject': 'NO_SUBJECT', 'body': 'NO_BODY', 'id': o['id']} 

    try:
        payload = o['payload']
        subject = [x['value'] for x in o['payload']['headers'] if x['name'] == 'Subject']

        if len(subject) > 0:
            return_msg['subject'] = subject[0]
    
        if 'parts' in payload:
            for p in payload['parts']:
                #print("Parts")
                if p['mimeType'] == 'text/plain':
                    decoded = base64.b64decode(p['body']['data'])
                    return_msg['body'] = decoded


        if payload['body']['size'] > 0:
            #print("Body")
            decoded = base64.b64decode(payload['body']['data'])
            return_msg['body'] = decoded

    except Exception as e:
        pass
        #print("error")
        #print(e)

    return return_msg


def parse_messages(msgs):
    result = []
    for m in msgs:
        result.append(parse_message(m))       

    return result


credential_file = 'credentials.json'
credential_text = open(credential_file).read()
credentials = OAuth2Credentials.from_json(credential_text)
service = build_service(credentials)

def process_messages():
    processed = 0
    page_limit = 500
    pageToken = ''
    errors = 0
    done = False
        
    #cmdline args
    mode = sys.argv[1] # delete, trash, dryrun

    if mode == "help":
        print("python2 api.py <mode> <query> <limit> (mode=delete|trash|dryrun)")
        exit(0)

    query = sys.argv[2]
    total_limit = int(sys.argv[3])

    if total_limit < page_limit:
        page_limit = total_limit


    id_list = []
    while (True):
        if pageToken is None or done == True: 
            break

        (thread_ids, pageToken) = get_message_ids(service, query, pageToken, page_limit)
        
        print("Found " + str(len(thread_ids)) + " messages found")
        #raw_input("Press enter to trash all.")

        if mode == "delete":
            print("Batch Deleting..." + str(len(thread_ids)) + " messages")
            batch_delete_messages(service, thread_ids)
            processed = processed + len(thread_ids)

            if processed >= total_limit:
                done = True
                break

        else:

            for thread_id in thread_ids:
                try:
                    processed = processed + 1
                    id_list.append(thread_id)

                    if mode == 'trash':
                        print(str(processed) + ". Trashing..." + str(thread_id))
                        trash_thread(service, thread_id)
                    elif mode == 'single-delete':
                        print(str(processed) + ". Deleting..." + str(thread_id))
                        delete_message(service, thread_id)
                    else:
                        print(str(processed) + ". Dry run..." + str(thread_id))

                except Exception as e:
                    errors = errors + 1
                    print("Error for thread: " + thread_id)
                    print(e)

                if processed >= total_limit:
                    done = True
                    break
        


    print("COMPLETED! Processed " + str(processed) + " messages");

    if errors > 0:
        print("Errors: " + str(errors))


process_messages()
    
