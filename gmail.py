import base64
import datetime
import httplib2
import os
import re
import time

from tqdm import tqdm
from infrastructure import settings
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
    scopes = 'https://www.googleapis.com/auth/gmail.readonly'
    cwd_dir = os.getcwd()
    client_secret_dir = os.path.join(cwd_dir, 'infrastructure')
    client_secret_file = os.path.join(client_secret_dir, 'oauth_client_id.json')
    credentials = get_credentials(client_secret_file, scopes)
    service = build_service(credentials)

    return service


def list_threads(service, label_ids):
    response = service.users().threads().list(userId='me', labelIds=label_ids).execute()

    threads = []
    if 'threads' in response:
        threads.extend(response['threads'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().threads().list(userId="me", labelIds=label_ids, pageToken=page_token).execute()
        threads.extend(response['threads'])

    return threads


def print_labels(service):
    response = service.users().labels().list(userId='me').execute()
    labels = response['labels']

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'] + "," + label['id'])


def get_threads(service, thread_list):
    for thread in tqdm(thread_list, disable=False):
        # print(thread['id'])
        thread = service.users().threads().get(userId="me", id=thread['id']).execute()
        for message in thread['messages']:
            correo = {}
            # print(message['id'])

            headers = message['payload']['headers']
            for header in headers:
                if header['name'] == 'Subject':
                    # print(f"Subject: {header['value']}")
                    correo['Subject'] = header['value']
                elif header['name'] == 'Date':
                    # print(f"Date: {header['value']}")
                    fecha = datetime.datetime.strptime(header['value'], "%a, %d %b %Y %H:%M:%S %z")
                    timestamp = fecha.strftime("%d%m%Y_%H%M%S")
                elif header['name'] == 'From':
                    # print(f"From: {re.findall(r'<(.*)>', header['value'])[0]}")
                    sender = re.findall(r'<(.*)>', header['value'])[0]

            if "multipart" in message['payload']['mimeType']:
                # print("multipart")
                for part in message['payload']['parts']:
                    # To read body
                    if part['mimeType'] == 'text/plain':
                        bytecode = bytes(str(part['body']['data']), encoding='utf-8')
                        # print(base64.urlsafe_b64decode(bytecode))
                    if part['mimeType'] == 'text/html':
                        bytecode = bytes(str(part['body']['data']), encoding='utf-8')
                        # print(base64.urlsafe_b64decode(bytecode))
                    # To download PDF attachments
                    if part['mimeType'] == 'application/pdf':
                        att_id = part['body']['attachmentId']
                        att = service.users().messages().attachments().get(userId="me",
                                                                           messageId=message['id'],
                                                                           id=att_id).execute()
                        data = att['data']
                        file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                        file_root = settings.conf[settings.mode]['files_root']
                        file_path = ''.join(
                            [file_root, "/",
                             timestamp, "/",
                             sender, "/",
                             thread['id'], "/",
                             message['id'], "/",
                             part['filename']]
                        )
                        # print(f"Attached PDF: {file_data}")
                        if not os.path.exists(os.path.dirname(file_path)):
                            try:
                                os.makedirs(os.path.dirname(file_path))
                            except OSError as e:  # Guard against race condition
                                if e.errno != errno.EEXIST:
                                    raise

                        if not os.path.exists(file_path):
                            with open(file_path, 'wb') as saved_file:
                                saved_file.write(file_data)
                                print(f"Saving {file_path}")
                                saved_file.close()
                        else:
                            pass
                            # print(f"File {part['filename']} already exists")

            else:
                # print("text")
                bytecode = bytes(str(message['payload']['body']['data']), encoding='utf-8')
                # print(base64.urlsafe_b64decode(bytecode))
                # print(message['payload']['body']['data'])
            # print(message['payload']['mimeType'])


def main():
    start = time.time()
    print(f"Execution start: {datetime.datetime.now()}")
    service = connect_gmail()
    print(service)
    thread_list = list_threads(service, [NEW_ORDERS_LABEL])
    print(f"Threads: {thread_list}")
    get_threads(service, thread_list)
    print(f"Execution took: {time.time() - start}")


if __name__ == '__main__':
    main()
