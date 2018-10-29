import base64
import email
import datetime
import errno

import httplib2
import os
import re

from apiclient import discovery
from apiclient import errors
from bs4 import BeautifulSoup
from infrastructure import settings
from oauth2client import file, client, tools
from tqdm import tqdm

PROCESSING_LABEL = 'Label_4220360407063600674'
NEW_ORDERS_LABEL = 'Label_7015697172796597976'

class GmailSrv:
    def __init__(self, scopes, client_secret_file):
        self.SCOPES = scopes
        self.CLIENT_SECRET_FILE = client_secret_file

    def get_credentials(self):
        cwd_dir = os.getcwd()
        credential_dir = os.path.join(cwd_dir, 'infrastructure')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)

        credential_path = os.path.join(credential_dir, 'gmail-credentials.json')

        store = file.Storage(credential_path)
        credentials = store.get()

        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            credentials = tools.run_flow(flow, store)
            print('Storing credentials to ' + credential_path)

        return credentials

    @staticmethod
    def build_service(credentials):
        http = httplib2.Http()
        http = credentials.authorize(http)

        return discovery.build('gmail', 'v1', http=http)

    @staticmethod
    def print_labels(service):
        response = service.users().labels().list(userId='me').execute()
        labels = response['labels']

        if not labels:
            print('No labels found.')
        else:
            print('Labels:')
            for label in labels:
                print(label['name'] + "," + label['id'])

    @staticmethod
    def get_label_messages(service, label_ids=[]):
        try:
            response = service.users().messages().list(userId='me', labelIds=label_ids).execute()
            # print(f"List label response: {response}")

            messages = []
            if 'messages' in response:
                # print(f"Messages: {response['messages']}")
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = service.users().messages().list(userId='me',
                                                           labelIds=label_ids,
                                                           pageToken=page_token).execute()
                messages.extend(response['messages'])

            orders = {}
            for message in messages:
                try:
                    orders[message['threadId']].append(message['id'])
                except KeyError:
                    orders[message['threadId']] = [message['id']]

            # print(f"Orders: {orders}")
            # print(len(orders))

            dated_orders = {}
            labels_bar = tqdm(orders.items(), unit="thread")
            labels_bar.set_description("Getting orders")
            for thread, message_list in labels_bar:
                for message_id in message_list:
                    # print(message_id)
                    message = service.users().messages().get(userId='me', id=message_id).execute()
                    headers = message['payload']['headers']
                    for header in headers:
                        if header['name'] == 'Date':
                            fecha = datetime.datetime.strptime(header['value'], "%a, %d %b %Y %H:%M:%S %z")
                            try:
                                dated_orders[thread].append((message_id, fecha))
                            except KeyError:
                                dated_orders[thread] = [(message_id, fecha)]

            sorted_orders = {}

            sorting_bar = tqdm(dated_orders.items())
            sorting_bar.set_description("Sorting emails")
            for key, value in sorting_bar:
                sorted_orders[key] = sorted(value, key=lambda x: x[-1])

            return sorted_orders

        except errors.HttpError as error:
            print('An error occurred: %s' % error)
    #
    # @staticmethod
    # def get_visible(element):
    #     if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
    #         return False
    #     elif re.match('<!--.*-->', str(element)):
    #         return False
    #     return True

    # @staticmethod
    # def remove_unicode_non_printable(entrada):
    #     return ''.join([ch for ch in entrada if (ord(ch) > 31 or ord(ch) == 9)])

    @staticmethod
    def get_message_details(service, message_id):
        # TODO: Scrape the first message when the customer forwards an email from a third party
        # print(f"Message ID: {message_id}")
        message = service.users().messages().get(userId='me', id=message_id).execute()
        # print(message)
        headers = message['payload']['headers']
        # print(headers)
        correo = {}

        for header in headers:
            if header['name'] == 'Subject':
                # print(f"Subject: {header['value']}")
                correo['Subject'] = header['value']
            elif header['name'] == 'Date':
                # print(f"Date: {header['value']}")
                correo['Date'] = datetime.datetime.strptime(header['value'], "%a, %d %b %Y %H:%M:%S %z")
            elif header['name'] == 'From':
                # print(f"From: {header['value']}")
                correo['From'] = [
                    header['value'].split("<")[0].replace("\"", ""),
                    re.findall(r'<(.*)>', header['value'])[0]
                ]
                # correo['From'] = header['value']

        raw_message = service.users().messages().get(userId='me', id=message_id, format='raw').execute()
        msg_str = str(base64.urlsafe_b64decode(raw_message['raw'].encode('ASCII')), 'UTF-8')
        mime_msg = email.message_from_string(msg_str)
        # print(mime_msg)
        message_main_type = mime_msg.get_content_maintype()
        # print(message_main_type)
        correo['Main_Type'] = message_main_type

        correo['Body_Txt'] = ""
        correo['Body_Html'] = ""
        if message_main_type == 'multipart':
            for part in mime_msg.walk():
                # print(f"PART START:\n\n {part}")
                # print(part.get_content_type())
                try:
                    if part.get_content_type() == 'text/plain':
                        # print(f"PART START:\n\n {part}")
                        soup = BeautifulSoup(part.get_payload(decode=True), 'lxml')
                        # print(f"Soup: {soup}")
                        texts = soup.find_all(text=True)
                        full_text = ''
                        if len(texts) >= 1:
                            # print(f"Text length: {len(texts)}")
                            for group in texts:
                                full_text += group
                                # print(f"Group: {group}")

                            # print(f"Full: {full_text}")
                            filtered_text = ''
                            for line in full_text.splitlines():
                                # print(f"Line: {line}")
                                if not line.startswith(">"):
                                    # print(f"Line: {line}")
                                    filtered_text += line + "\n"

                            # print(f"Filtered: {filtered_text}")
                            correo['Type'] = part.get_content_type()
                            correo['Body_Txt'] = filtered_text
                            correo['Parsing'] = "Success"

                    elif part.get_content_type() == 'text/html':
                        correo['Type'] = part.get_content_type()
                        correo['Body_Html'] = BeautifulSoup(part.get_payload(decode=True), 'lxml')
                        # print("#########################################################")
                        # print(f"\n\n{message_id}")
                        # print(correo['Body_Html'])
                        correo['Parsing'] = "Success"

                except Exception as e:
                    print(e)

        elif message_main_type == 'text':
            # TODO: Resolve issue with messages from AIT (166463a364098596, 1665851a6e5128a7)
            # correo['Body_Txt'] = mime_msg.get_payload(decode=True)
            soup = BeautifulSoup(mime_msg.get_payload(decode=True), 'lxml')
            # print(f"Soup: {soup}")
            texts = soup.find_all(text=True)
            full_text = ''
            if len(texts) >= 1:
                # print(f"Text length: {len(texts)}")
                for group in texts:
                    full_text += group
                    # print(f"Group: {group}")

                # print(f"Full: {full_text}")
                filtered_text = ''
                for line in full_text.splitlines():
                    # print(f"Line: {line}")
                    if not line.startswith(">"):
                        # print(f"Line: {line}")
                        filtered_text += line + "\n"

                # print(f"Filtered: {filtered_text}")
                correo['Type'] = message_main_type
                correo['Body_Txt'] = filtered_text
                correo['Parsing'] = "Success"
            # print(message_id)
            # print(correo['Body_Txt'])

        return correo

    @staticmethod
    def download_mssg_attachments(service, order, mssg_id):
        message = service.users().messages().get(userId="me", id=mssg_id).execute()
        # print(f"Message payload type: {type(message['payload'])}")
        try:
            headers = message['payload']['headers']
            # print(headers)
            # TODO: Improve this code (this repeats message details segment)
            for header in headers:
                if header['name'] == 'From':
                    sender = re.findall(r'<(.*)>', header['value'])[0]
                    # print(f"Sender: {sender}")
                elif header['name'] == 'Date':
                    # print(f"Date: {header['value']}")
                    fecha = datetime.datetime.strptime(header['value'], "%a, %d %b %Y %H:%M:%S %z")
                    timestamp = fecha.strftime("%d%m%Y_%H%M%S")

            attachments = []
            for part in message['payload']['parts']:
                new_var = part['body']
                if 'attachmentId' in new_var:
                    att_id = new_var['attachmentId']
                    att = service.users().messages().attachments().get(userId="me",
                                                                       messageId=mssg_id,
                                                                       id=att_id).execute()
                    data = att['data']
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    # print(part['filename'])
                    # TODO: Save the files into its respective path
                    file_root = settings.conf[settings.mode]['files_root']
                    file_path = ''.join(
                        [file_root, "/",
                         timestamp, "/",
                         sender, "/",
                         order, "/",
                         mssg_id, "/",
                         part['filename']]
                    )

                    if not os.path.exists(os.path.dirname(file_path)):
                        try:
                            os.makedirs(os.path.dirname(file_path))
                        except OSError as e:  # Guard against race condition
                            if e.errno != errno.EEXIST:
                                raise

                    if not os.path.exists(file_path):
                        with open(file_path, 'wb') as saved_file:
                            saved_file.write(file_data)
                            saved_file.close()
                    else:
                        pass
                        # print(f"File {part['filename']} already exists")

                    # print(f"Attachment path:  {file_path}")
                    attachments.append([part['filename'], file_path])
            return attachments

        except Exception as e:
            print(e)
            return []

    @staticmethod
    def mark_as_read(service, mssg_id):
        try:
            mssg_labels = {'removeLabelIds': [NEW_ORDERS_LABEL], 'addLabelIds': [PROCESSING_LABEL]}
            service.users().messages().modify(userId="me",
                                              id=mssg_id,
                                              body=mssg_labels).execute()
        except errors.HttpError as error:
            print('An error occurred: %s' % error)
