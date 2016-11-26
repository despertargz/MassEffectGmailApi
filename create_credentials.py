from __future__ import print_function

import httplib2
import os
import json
import sys

import base64
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import AccessTokenCredentials

from apiclient.discovery import build



#result = get_authorization_url('mev412@gmail.com', 'nope', 'secret.json', scope);


authorization_code = sys.argv[1]
#authorization_code = '4/CMf5Bl7CZB1MPpLhpY2ZgomVnaZEWC0LWTS8RSPUGow'

credential_file = 'credentials.json'
secret_file = 'secret.json'
email_address = 'mev412@gmail.com'
state='nope'
scope = 'https://www.googleapis.com/auth/gmail.modify https://www.googleapis.com/auth/gmail.modify'

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
save_creds()

