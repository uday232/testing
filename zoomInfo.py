import csv
import os
import shutil
import time
import uuid
import sys
from datetime import datetime

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



def open_gmail(driver):
    wait = WebDriverWait(driver, 120)
    driver.execute_script("window.open('https://www.google.com/gmail/about/')")
    # driver.get("https://www.google.com/gmail/about/")
    time.sleep(1)
    window_handles = driver.window_handles
    second_window_handle = window_handles[1]
    driver.switch_to.window(second_window_handle)
    driver.implicitly_wait(120)
    driver.find_element(By.XPATH, "//a[text()='Sign in']").is_displayed()
    driver.find_element(By.XPATH, "//a[text()='Sign in']").click()
    print("Sign In Button Clicked")
    time.sleep(2)
    driver.implicitly_wait(120)
    driver.find_element(By.XPATH, "//input[@type='email']").is_displayed()
    driver.find_element(By.XPATH, "//input[@type='email']").send_keys("lila.davis@vassardigital.ai")
    print("User ID Entered")
    time.sleep(1)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button//span[text()='Next']")))
    driver.find_element(By.XPATH,
                        "//button//span[text()='Next']").is_enabled()
    driver.find_element(By.XPATH,
                        "//button//span[text()='Next']").click()
    print("next button clicked")
    time.sleep(2)
    driver.implicitly_wait(120)
    driver.find_element(By.XPATH, "//input[@type='password']").is_displayed()
    time.sleep(1)
    driver.find_element(By.XPATH, "//input[@type='password']").click()
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys("Future@Labs2023")
    time.sleep(1)
    print("password entered")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button//span[text()='Next']")))
    driver.find_element(By.XPATH,
                        "//button//span[text()='Next']").is_enabled()
    driver.find_element(By.XPATH,
                        "//button//span[text()='Next']").click()
    print("next button clicked")
    time.sleep(2)
    driver.implicitly_wait(30)
    driver.find_element(By.XPATH, "//div[text()='Compose']").is_displayed()
    print("email opened")



def get_authentication_code(driver):
    window_handles = driver.window_handles
    second_window_handle = window_handles[1]
    driver.switch_to.window(second_window_handle)
    wait = WebDriverWait(driver, 120)
    wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//button[@data-tooltip='Show search options']//*[local-name()='svg']//*[local-name()='path']")))
    driver.find_element(By.XPATH,
                        "//button[@data-tooltip='Show search options']//*[local-name()='svg']//*[local-name()='path']").click()
    time.sleep(1)
    wait.until(
        EC.visibility_of_element_located((By.XPATH, "//label[text()='Subject']//parent::span//parent::div//input")))
    driver.find_element(By.XPATH, "//label[text()='Subject']//parent::span//parent::div//input").clear()
    driver.find_element(By.XPATH, "//label[text()='Subject']//parent::span//parent::div//input").send_keys(
        "One-time verification code")
    print("search")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Search' and @role='button']")))
    driver.find_element(By.XPATH, "//div[text()='Search' and @role='button']").is_enabled()
    driver.find_element(By.XPATH, "//div[text()='Search' and @role='button']").click()
    time.sleep(2)
    date_flag = True
    while date_flag:
        driver.implicitly_wait(120)
        driver.find_element(By.XPATH, "//div[@role='main']//table//tbody//tr").is_displayed()
        present_date = datetime.now().strftime("%a, %b %-d, %Y")
        print(present_date, " prst date")
        driver.implicitly_wait(3)
        color_size = len(driver.find_elements(By.XPATH,
                                              "//div[@role='main']//table//tbody//tr//td[8]//span[contains(@title,'" + present_date + "')]//ancestor::tr[contains(@class,'zA zE')]"))
        print(color_size)
        if color_size > 0:
            print("inside if")
            date_flag = False
        else:
            time.sleep(5)
            # driver.find_element(By.XPATH, "//div[@role='main']//div[@aria-label='Refresh']").click()
            driver.refresh()
            wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//label[text()='Subject']//parent::span//parent::div//input")))
            driver.find_element(By.XPATH, "//label[text()='Subject']//parent::span//parent::div//input").clear()
            driver.find_element(By.XPATH, "//label[text()='Subject']//parent::span//parent::div//input").send_keys(
                "One-time verification code")
            print("search")
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Search' and @role='button']")))
            driver.find_element(By.XPATH, "//div[text()='Search' and @role='button']").is_enabled()
            driver.find_element(By.XPATH, "//div[text()='Search' and @role='button']").click()
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='main']//table//tbody//tr//td[5]")))
    # driver.find_element(By.XPATH, "//div[@role='main']//table//tbody//tr//td[5]").is_displayed()
    emails = driver.find_elements(By.XPATH, "//div[@role='main']//table//tbody//tr//td[5]")
    emails[0].click()
    print("inside email")
    time.sleep(2)
    code = driver.find_elements(By.XPATH, "//span[contains(@id,'verification-code')]")[-1].text
    print("code stored")
    # print(code)
    time.sleep(2)
    first_window_handle = window_handles[0]
    driver.switch_to.window(first_window_handle)
    return code





options = Options()
options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
options.add_argument('window-size=1200x600')
driver = webdriver.Chrome(options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 120)
# driver.get('https://login.zoominfo.com/')
# time.sleep(1)
# data = list(
#     ContactInfo.objects.annotate(customer_name=F('customer_id__customer_name')).filter(
#         zoominfo_scraping_status__isnull=True).values('linkedin_id_url',
#                                                         'customer_id',
#                                                         'first_name',
#                                                         'last_name',
#                                                         'customer_name'))
# print(len(data), " data")
# driver.implicitly_wait(30)
# driver.find_element(By.ID, 'okta-signin-username').is_displayed()
# driver.find_element(By.ID, 'okta-signin-username').send_keys("lila.davis@vassardigital.ai")
# driver.find_element(By.ID, "okta-signin-password").send_keys("Future@Labs2024")
# time.sleep(2)
# driver.find_element(By.XPATH, "//input[@id='okta-signin-submit']").is_enabled()
# driver.find_element(By.XPATH, "//input[@id='okta-signin-submit']").click()
# time.sleep(2)
open_gmail(driver)
code = get_authentication_code(driver)
print(code)
# driver.find_element(By.XPATH, "//input[@id='verify-code-input']").send_keys(code)
# print("code entered")
# time.sleep(2)
# driver.find_element(By.XPATH, "//button[text()='Verify']").click()
# driver.implicitly_wait(120)
# driver.find_element(By.XPATH,
#                     "//button[contains(text(),'Advanced Search')]//parent::div//parent::div//input").is_displayed()
# print("inside zoominfo")
# driver.implicitly_wait(1)
# popup_size = len(driver.find_elements(By.XPATH, "//button[contains(@class,'pendo-close-guide')]"))
# if popup_size > 0:
#     driver.find_element(By.XPATH, "//button[contains(@class,'pendo-close-guide')]").click()
#     time.sleep(1)

# users_not_found = []
# zoominfo_scraping_status = None
# zoominfo_scraping_url = None




