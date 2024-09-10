import csv
import os
import shutil
import time
import uuid
import sys

# import pandas as pd
# import requests
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


def ClickOnExport():
    print("ok")
    options = Options()
    options.add_argument("--headless")
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    options.add_argument('window-size=1200x600')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    # wait = WebDriverWait(driver, 120)
    # driver.get('https://app.dripify.io/')
    # time.sleep(1)
    # driver.implicitly_wait(180)
    # driver.find_element(By.ID, "email").is_displayed()
    # driver.find_element(By.ID, "email").send_keys("lputta@vassarlabs.com")
    # time.sleep(1)
    # driver.find_element(By.ID, "password").send_keys("Future@Labs2023")
    # time.sleep(1)
    # driver.find_element(By.XPATH, "//button[@type='submit']").is_enabled()
    # driver.find_element(By.XPATH, "//button[@type='submit']").click()
    # driver.implicitly_wait(180)
    # driver.find_element(By.XPATH, "//h2[text()='Statistics']").is_displayed()
    # time.sleep(2)
    # print("inside dripify")
    # driver.find_element(By.ID, "leads-link").click()
    # time.sleep(3)
    # print("clicked on leads")
    # driver.find_element(By.XPATH, "//button[contains(@class, 'async-btn')]").click()
    # time.sleep(10)


# def open_gmail():

#     options = Options()
#     # options.add_argument("--headless")
#     options.add_argument(
#         'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
#     options.add_argument('window-size=1200x600')
#     driver = webdriver.Chrome(options=options)
#     driver.maximize_window()
#     wait = WebDriverWait(driver, 120)
#     driver.execute_script("window.open('https://www.google.com/gmail/about/')")
#     time.sleep(1)
#     window_handles = driver.window_handles
#     second_window_handle = window_handles[1]
#     driver.switch_to.window(second_window_handle)
#     driver.implicitly_wait(120)
#     driver.find_element(By.XPATH, "//a[text()='Sign in']").is_displayed()
#     driver.find_element(By.XPATH, "//a[text()='Sign in']").click()
#     print("Sign In Button Clicked")
#     time.sleep(2)
#     driver.implicitly_wait(120)
#     driver.find_element(By.XPATH, "//input[@type='email']").is_displayed()
#     driver.find_element(By.XPATH, "//input[@type='email']").send_keys("lila.davis@vassardigital.ai")
#     print("User ID Entered")
#     time.sleep(1)
#     wait.until(EC.element_to_be_clickable((By.XPATH, "//button//span[text()='Next']")))
#     driver.find_element(By.XPATH,
#                         "//button//span[text()='Next']").is_enabled()
#     driver.find_element(By.XPATH,
#                         "//button//span[text()='Next']").click()
#     print("next button clicked")
#     time.sleep(2)
#     driver.implicitly_wait(120)
#     driver.find_element(By.XPATH, "//input[@type='password']").is_displayed()
#     time.sleep(1)
#     driver.find_element(By.XPATH, "//input[@type='password']").click()
#     driver.find_element(By.XPATH, "//input[@type='password']").send_keys("Future@Labs2023")
#     time.sleep(1)
#     print("password entered")
#     wait.until(EC.element_to_be_clickable((By.XPATH, "//button//span[text()='Next']")))
#     driver.find_element(By.XPATH,
#                         "//button//span[text()='Next']").is_enabled()
#     driver.find_element(By.XPATH,
#                         "//button//span[text()='Next']").click()
#     print("next button clicked")
#     time.sleep(2)
#     driver.implicitly_wait(30)
#     driver.find_element(By.XPATH, "//div[text()='Compose']").is_displayed()
#     print("email opened")


# open_gmail()
ClickOnExport()
