import base64
from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

import email
from email.header import decode_header
import imaplib
import json
import re


gmail_username='lila.davis@vassardigital.ai'
gmail_password = 'xcdg ymlx wgyi edgv'
gmail_host_data = 'imap.gmail.com'
gmail_port_data = 993



def login_to_gmail(username, password):
    print("Login to Gmail")
    gmail_host = gmail_host_data
    gmail_port = gmail_port_data
    try:
        mail = imaplib.IMAP4_SSL(gmail_host, gmail_port)
        mail.login(username, password)
        print("Email Data checking...")
        print(mail)
        print(mail.response)
        print("Login successful.")
        return mail
    except Exception as e:
        print(f"Error: {e}")
        return None



def fetch_csv(mail):
    print("Fetching email data...")
    mail.select('inbox')
    status, messages = mail.search(None, '(UNSEEN from "support@dripify.io")')
    fetched_emails = []
    helpdesk_mails=[]
    if status == 'OK' and messages[0]:
        for index, message in enumerate(messages[0].split()[::-1]):
            if index >= 2:
                break
            _, msg_data = mail.fetch(message, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    email_message = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(email_message["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")
                    email_from = email_message.get("From")
                    email_to = email_message.get("To")
                    message_id = email_message.get("Message-ID", None)
                    in_reply_to = email_message.get("In-Reply-To", None)
                    references = email_message.get("References", None)
                    date = email_message.get("Date", None)
                    attachments = extract_attachments(email_message)
                    for attachment in attachments:
                        save_attachment(attachment,"Documents")


                    # Get email body
                    # body = ''
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            content_type = part.get_content_type()
                            if content_type == 'text/plain':
                                body = part.get_payload(decode=True).decode(part.get_content_charset(), errors='ignore')
                            elif content_type == 'application/octet-stream':
                                attachment = {
                                    'filename': part.get_filename(),
                                    'data': base64.b64encode(part.get_payload(decode=True)).decode()
                                }
                                attachments.append(attachment)
                    else:
                        body = email_message.get_payload(decode=True).decode()

                    fetched_emails.append({
                        "email_from": email_from,
                        "email_to": email_to,
                        "message_id": message_id,
                        "subject": subject,
                        "in_reply_to": in_reply_to,
                        "references": references,
                        "date": date,
                        "email_body": body,
                        "is_incoming": True
                    })
    else:
        print("No emails found.")
    return fetched_emails


def extract_attachments(email_message):
    attachments = []

    for part in email_message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue

        filename = part.get_filename()
        content_type = part.get_content_type()

        if filename or content_type:
            print(filename)
            attachments.append({
                "filename": filename,
                "content_type": content_type,
                "data": part.get_payload(decode=True),
            })

    return attachments



def save_attachment(attachment,folder):
    # Save the attachment data to a file
    # print(attachment["filename"])
    filename = attachment["filename"]
    filename = filename.replace(' ','_')
    data = attachment["data"]

    folder_path = os.path.join(BASE_DIR,f"attachments/{folder}/")
    
    if not os.path.exists(os.path.dirname(folder_path)):
        # If not, create it
        print("creating folder")
        os.makedirs(os.path.dirname(folder_path))

    file_path = os.path.join(folder_path,filename)

    print(file_path)

    with open(file_path, 'wb') as file:
        file.write(data)
        print(f"    Saved to: {file_path}")

mail=login_to_gmail(gmail_username, gmail_password)
fetched_data=fetch_csv(mail)



# def retrieve_otp_from_email():
#     mail=login_to_gmail(gmail_username, gmail_password)
#     fetched_data=fetch_first_two_emails(mail)
#     # print(fetched_data)

#     # print(len(fetched_data))
#     for i in range(len(fetched_data)):
#         body_email=fetched_data[i]['email_body']

        
#         otp = re.findall(r'\b\d{6}\b', body_email)
#         if otp:
#             return otp[0]
#     return "No OTP found"

# otp=retrieve_otp_from_email()
# print(otp)

