import csv
import os
import shutil
import time
import uuid
import sys

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
from bs4 import BeautifulSoup

api_key = "4562a7f245fc40459418d566863bfb84"


def RetrieveMessage(name_of_connection):

    options = Options()
    # options.add_argument("--headless")
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    options.add_argument('window-size=1200x600')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 120)
    driver.get('https://app.dripify.io/')
    time.sleep(1)
    # window_handles = driver.window_handles
    # second_window_handle = window_handles[1]
    # driver.switch_to.window(second_window_handle)
    driver.implicitly_wait(180)
    driver.find_element(By.ID, "email").is_displayed()
    driver.find_element(By.ID, "email").send_keys("lputta@vassarlabs.com")
    time.sleep(1)
    driver.find_element(By.ID, "password").send_keys("Future@Labs2023")
    time.sleep(1)
    driver.find_element(By.XPATH, "//button[@type='submit']").is_enabled()
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    driver.implicitly_wait(180)
    driver.find_element(By.XPATH, "//h2[text()='Statistics']").is_displayed()
    time.sleep(2)
    print("inside dripify")
    driver.find_element(By.ID, "leads-link").click()
    time.sleep(3)
    print("clicked on leads")
    time.sleep(3)
    driver.find_element(By.ID, "searcher").send_keys(name_of_connection)
    time.sleep(3)
    driver.find_element(By.CSS_SELECTOR, "a.lead-item__main").click()
    time.sleep(2)
    driver.find_element(By.CSS_SELECTOR, "a.btn.btn--base.btn--to-icon-on-fablet.btn--auto-w").click()
    time.sleep(5)

    conversation_html = driver.find_element(By.CLASS_NAME, "conversation__content").get_attribute("outerHTML")

    # Parse the HTML using BeautifulSoup
    # soup = BeautifulSoup(conversation_html, 'html.parser')

    # Write the HTML to a file
    with open('messages.html', 'w') as file:
        file.write(conversation_html)


def ExtractMessages(name_of_connection):
    # Read the HTML file
    with open('messages.html', 'r') as file:
        html = file.read()

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Find all the messages
    messages = soup.find_all('div', class_='msg')
    date=""
    for message in messages:
        name=name_of_connection
        if message['aria-label'] == 'Outcome message':
            name="You"
        date_new = message.find_all('time', class_='msg__new-day')
        if len(date_new) > 0:
            date = date_new[0]
        message_body=message.find_all('div',class_='msg__content')[0]
        final_message=message_body.find_all('p')[0]
        time = message.find_all('time', class_='msg-time')[0]

        print(name+":")
        print(date)
        print(time)
        print(final_message)  
    

RetrieveMessage("Hakan Kostepen")
ExtractMessages("Hakan Kostepen")

