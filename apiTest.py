import csv
import os
import shutil
import time
import uuid
import sys
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
import pandas as pd
import requests
# from django.core.exceptions import ObjectDoesNotExist
# from django.core.files.uploadedfile import InMemoryUploadedFile
# from django.db import transaction
# from django.shortcuts import get_object_or_404
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
# from django.db.models import F, Q
# import logging
# from datetime import datetime
from selenium.webdriver.support import expected_conditions as EC, wait

from selenium.webdriver.support.wait import WebDriverWait

# from sales.models import CustomerInfo, ContactInfo, CampaignInfo, SalesPersonInfo, CampaignSalesPersonMappingInfo, \
#     LinkedInTemplate, LinkedInTouchPoints, EmailTemplate, EmailTouchPoints, PhoneTouchPoints, \
#     CampaignContactMappingInfo, CronJobInfo
from selenium.webdriver.chrome.options import Options  # Note: Capital "O" in "Options"

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

api_key = "4562a7f245fc40459418d566863bfb84"


def DripifyTest():
    options = Options()
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    options.add_argument('window-size=1200x600')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 120)
    driver.get('https://app.dripify.io/')
    time.sleep(1)
    driver.implicitly_wait(180)
    driver.find_element(By.ID, "email").is_displayed()
    driver.find_element(By.ID, "email").send_keys("lputta@vassarlabs.com")
    time.sleep(1)
    driver.find_element(By.ID, "password").send_keys("Future@Labs2023")
    time.sleep(1)
    driver.find_element(By.XPATH, "//button[@type='submit']").is_enabled()
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    driver.implicitly_wait(180)
    time.sleep(2)
    return driver.find_element(By.XPATH, "//h2[text()='Statistics']").is_displayed()


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



def fetch_first_two_emails(mail):
    print("Fetching email data...")
    mail.select('inbox')
    status, messages = mail.search(None, '(UNSEEN FROM "helpmenow@zoominfo.com")')
    fetched_emails = []
    helpdesk_mails=[]
    if status == 'OK' and messages[0]:
        for index, message in enumerate(messages[0].split()[::-1]):
            if index >= 1:
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
                    # attachments = extract_attachments(email_message)


                    # Get email body
                    # body = ''
                    if email_message.is_multipart():
                        for part in email_message.walk():
                            content_type = part.get_content_type()
                            if content_type == 'text/plain':
                                body = part.get_payload(decode=True).decode(part.get_content_charset(), errors='ignore')
                            # elif content_type == 'application/octet-stream':
                                # attachment = {
                                #     'filename': part.get_filename(),
                                #     'data': base64.b64encode(part.get_payload(decode=True)).decode()
                                # }
                                # attachments.append(attachment)
                    else:
                        body = email_message.get_payload(decode=True).decode()

                    # for file in attachments:
                    #     save_attachment(file,"Documents")
                    

                    # Print email body for reference
                    # print("Email Body:")
                    # print(email_body)
                    # print("email Body ends ::")

                    # if email_from == "helpmenow <helpmenow@zoominfo.com>":
                    # print("Email From: ", email_from)
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




def retrieve_otp_from_email():
    mail=login_to_gmail(gmail_username, gmail_password)
    fetched_data=fetch_first_two_emails(mail)
    # print(fetched_data)

    # print(len(fetched_data))
    for i in range(len(fetched_data)):
        body_email=fetched_data[i]['email_body']

        
        otp = re.findall(r'\b\d{6}\b', body_email)
        if otp:
            return otp[0]
    return "No OTP found"

def ZoomInfo():
    options = Options()
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    options.add_argument('window-size=1200x600')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get("https://login.zoominfo.com/")
    time.sleep(2)
    print("opened zoom info")

    driver.find_element(By.ID, 'okta-signin-username').is_displayed()
    driver.find_element(By.ID, 'okta-signin-username').send_keys("lila.davis@vassardigital.ai")
    driver.find_element(By.ID, "okta-signin-password").send_keys("Future@Labs2024")
    time.sleep(2)
    driver.find_element(By.XPATH, "//input[@id='okta-signin-submit']").is_enabled()
    driver.find_element(By.XPATH, "//input[@id='okta-signin-submit']").click()
    time.sleep(10)
    
    code= retrieve_otp_from_email()
    time.sleep(5)
    driver.find_element(By.XPATH, "//input[@id='verify-code-input']").send_keys(code)
    print("code entered")
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[text()='Verify']").click()
    driver.implicitly_wait(120)
    driver.find_element(By.XPATH,
                        "//button[contains(text(),'Advanced Search')]//parent::div//parent::div//input").is_displayed()
    print("inside zoominfo")
    return True
    

    
def ApolloTest():
    options = Options()
    # options.add_argument("--headless")
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/91.0.4472.124 Safari/537.36')
    options.add_argument('window-size=1200x600')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 120)
    driver.get('https://app.apollo.io/#/login')
    time.sleep(3)
    # print(len(data), " data ")
    
    # driver.implicitly_wait(120)
    driver.find_element(By.NAME, 'email').is_displayed()
    driver.find_element(By.NAME, 'email').send_keys("amit@vassarlabs.com")
    time.sleep(1)
    driver.find_element(By.NAME, "password").is_displayed()
    driver.find_element(By.NAME, "password").send_keys("Future@Labs2023")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
    time.sleep(2)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    driver.implicitly_wait(120)
    driver.find_element(By.ID, "side-nav-search").is_displayed()
    time.sleep(2)
    return True

    



def AdminConfigCheck():
    # if DripifyTest()==True:
    #     print("Dripify Test Passed")
    # else:
    #     print("Dripify Test Failed")
    # ZoomInfo()
    if ZoomInfo()==True:
        print("Here is the OTP:", retrieve_otp_from_email())
        print("ZoomInfo Test Passed")
    else:
        print("ZoomInfo Test Failed")

    # if ApolloTest()==True:
    #     print("Apollo Test Passed")
    # else:
    #     print("Apollo Test Failed")

AdminConfigCheck()

