from __future__ import print_function

import httplib2
import os
import json

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
scope = 'https://www.googleapis.com/auth/gmail.readonly'
#result = get_authorization_url('mev412@gmail.com', 'nope', 'secret.json', scope);


authorization_code = '4/zvVI49bvFyNB54vfHwVOfl6SbWw1Qwi51aUuofwIchM'

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

# save credentials
#save_creds()

# read credentials
credential_text = open(credential_file).read()
credentials = AccessTokenCredentials.from_json(credential_text)
#print(credentials)


service = build_service(credentials)
print(service)

result = service.users().messages().list(userId='me').execute()
msgs = result.get('messages', [])
for m in msgs:
    print(m)
    o = service.users().messages().get(userId='me', id=m['id']).execute()
    print(o)
    #print(m['payload']['body'])







