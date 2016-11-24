from __future__ import print_function
import httplib2
import os

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

def get_authorization_url(email_address, secret_file, scopes, redirect_url):
    flow = client.flow_from_clientsecrets(secret_file, scopes)
    flow.params['access_type'] = 'offline'
    flow.params['approval_prompt'] = 'force'
    flow.params['user_id'] = email_address
    flow.params['state'] = 'nope'
    return flow.step1_get_authorize_url(redirect_url)


redirect_url = 'http://googleapi.sonyar.info'

#scope = 'https://www.googleapis.com/auth/gmail.readonly'
scope = 'https://www.googleapis.com/auth/gmail.modify'

url = get_authorization_url('mev412@gmail.com', 'secret.json', scope, redirect_url);
print(url)



