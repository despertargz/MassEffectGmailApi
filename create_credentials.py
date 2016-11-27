from __future__ import print_function

import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.discovery import build

#1 - get authorize url
#2 - navigate to authorize url + grant permissions to the app
#3 - redirect to redirect_url with authorize_code passed in query string ?code=
#4 - exchange code for credentials, credentials.to_json() and from_json() can be used to save and retrieve
#5 - use credentials to authenticate and use gmail api

# cmdline args
email_address = sys.argv[1]

# constants
secret_file = 'secret.json'
credential_file = 'credentials.json'
#scope = 'https://www.googleapis.com/auth/gmail.modify'
#scope = 'https://www.googleapis.com/auth/gmail.readonly'
scope = 'https://mail.google.com'

flow = client.flow_from_clientsecrets(secret_file, scope)
flow.params['user_id'] = email_address
flow.params['access_type'] = 'offline'
flow.params['approval_prompt'] = 'force'
flow.params['state'] = 'nope'


def get_authorization_url(email_address, secret_file, redirect_url):
    return flow.step1_get_authorize_url(redirect_url)


def save_creds(authorization_code):
    credentials = flow.step2_exchange(authorization_code)
    f = open(credential_file, 'w')
    f.write(credentials.to_json())
    f.close()


redirect_url = 'http://googleapi.sonyar.info'

url = get_authorization_url('mev412@gmail.com', scope, redirect_url);
print(url)

auth_code = raw_input("Navigate to above url in browser, grant permissions, after redirect paste the code from the query string: ")
# save credentials
save_creds(auth_code)



