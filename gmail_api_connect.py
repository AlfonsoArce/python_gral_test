"""
    Script to connect to GMAIL using the API
"""
import datetime
import httplib2
import os
import time

from apiclient import discovery
from oauth2client import file, client, tools

NEW_ORDERS_LABEL = 'Label_7015697172796597976'


def get_credentials(client_secret_file, scopes):
    cwd_dir = os.getcwd()
    credential_dir = os.path.join(cwd_dir, 'infrastructure')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)

    credential_path = os.path.join(credential_dir, 'gmail-credentials.json')
    store = file.Storage(credential_path)
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secret_file, scopes)
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)

    return credentials


def build_service(credentials):
    http = httplib2.Http()
    http = credentials.authorize(http)

    return discovery.build('gmail', 'v1', http=http)


def connect_gmail():
    """
        Function to connect to GMAIL
    """
    scopes = 'https://www.googleapis.com/auth/gmail.readonly'
    cwd_dir = os.getcwd()
    # All the keys to connect to the API are under ./infrastructure
    client_secret_dir = os.path.join(cwd_dir, 'infrastructure')
    client_secret_file = os.path.join(client_secret_dir, 'oauth_client_id.json')
    credentials = get_credentials(client_secret_file, scopes)
    service = build_service(credentials)

    return service


def main():
    start = time.time()
    print(f"Execution start: {datetime.datetime.now()}")
    service = connect_gmail()
    print(service)
    print(f"Execution took: {time.time() - start}")


if __name__ == '__main__':
    main()
