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
from oauth2client.client import AccessTokenCredentials

from apiclient.discovery import build



def build_service(credentials):
  """Build a Gmail service object.

  Args:
    credentials: OAuth 2.0 credentials.

  Returns:
    Gmail service object.
  """
  http = httplib2.Http()
  http = credentials.authorize(http)
  return build('gmail', 'v1', http=http)

def get_authorization_url(email_address, state, secret_file, scopes):
  """Retrieve the authorization URL.

  Args:
    email_address: User's e-mail address.
    state: State for the authorization URL.
  Returns:
    Authorization URL to redirect the user to.
  """
  return flow.step1_get_authorize_url(REDIRECT_URL)


REDIRECT_URL = 'http://googleapi.sonyar.info'
scope = 'https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.readonly'
#result = get_authorization_url('mev412@gmail.com', 'nope', 'secret.json', scope);


authorization_code = '4/Jgo5Z3UpKNZ4fBX6bLhn-9P8DJOH089R55TpDwyGgLg'

credential_file = 'credentials.json'
secret_file = 'secret.json'
email_address = 'mev412@gmail.com'
state='nope'

flow = client.flow_from_clientsecrets(secret_file, scope)
flow.params['access_type'] = 'offline'
flow.params['approval_prompt'] = 'force'
flow.params['user_id'] = email_address
flow.params['state'] = state
flow.redirect_uri = 'http://googleapi.sonyar.info'

def save_creds():
    credentials = flow.step2_exchange(authorization_code)
    f = open(credential_file, 'w')
    f.write(credentials.to_json())
    f.close()



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


def trash_message(service, id):
    service.users().messages().trash(userId='me', id=id).execute()

# read credentials
credential_text = open(credential_file).read()
credentials = AccessTokenCredentials.from_json(credential_text)
#print(credentials)


service = build_service(credentials)

label_name = sys.argv[1]
label_id = get_label_id_from_name(service, label_name)


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

dry_run = 1
pageToken = ''
processed = 0
max_results = 1000

while (True):
    (msgs, pageToken) = get_thread_ids(service, label_id, pageToken, max_results)
    
    print("Found " + str(len(msgs)) + " threads under the label: " + label_name)
    #raw_input("Press enter to trash all.")

    for m in msgs:
        processed = processed + 1
        if dry_run == True:
            print(str(processed) + ". dry run, not trashing..." + str(m))
        else:
            print(str(processed) + ". trashing..." + str(m))
            trash_message(service, m)

    if pageToken is None: 
        break



print("COMPLETED! Processed " + str(processed) + " messages");
