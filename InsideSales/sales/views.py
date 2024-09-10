import csv
import os
import shutil
import time
import uuid
import sys
import random
import pandas as pd
import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from django.db.models import F, Q
from django.utils import timezone
import logging
from datetime import datetime,date
from selenium.webdriver.support import expected_conditions as EC, wait
from .serializers import PhoneTouchPointsSerializer, EmailTouchPointsSerializer, LinkedInTouchPointsSerializer, CampaignInfoSerializer

from selenium.webdriver.support.wait import WebDriverWait

from sales.models import CustomerInfo, ContactInfo, CampaignInfo, SalesPersonDetails, SalesPersonInfo, CampaignSalesPersonMappingInfo, \
    LinkedInTemplate, LinkedInTouchPoints, EmailTemplate, EmailTouchPoints, PhoneTouchPoints, \
    CampaignContactMappingInfo, CronJobInfo, MeetingTouchpoint, Note
from selenium.webdriver.chrome.options import Options  # Note: Capital "O" in "Options"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from django.http import HttpResponse
import json

api_key = "4562a7f245fc40459418d566863bfb84"

#for apis and IMAP 
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


def company_comparision(ui_name, db_name):
    db_name = db_name.replace("Corporation", "").strip()
    db_name = db_name.replace(", Inc.", "").strip()
    ui_name = ui_name.replace("Corporation", "").strip()
    ui_name = ui_name.replace(", Inc.", "").strip()
    # Case 1: Convert both names to lowercase and check the values
    if ui_name.lower() == db_name.lower():
        print("Case 1: Both names are equal when converted to lowercase.")
        company_status = "matching"
    elif len(ui_name.split()) == 1 and len(db_name.split()) > 1:
        # Case 2: ui_company_name has only one word and db_company_name has more than one word
        # Convert the company names by picking the first letter of each word
        ui_company_name_modified = ui_name.lower()
        db_company_name_modified = ''.join(
            [word[0] for word in db_name.split()]).lower()

        # Check whether the modified names are the same
        if ui_company_name_modified == db_company_name_modified:
            print("Case 2: Modified names are equal when converted to lowercase.")
            company_status = "matching"
        else:
            print("Case 2: Modified names are not equal when converted to lowercase.")
            print(ui_company_name_modified, " ui")
            print(db_company_name_modified, " db")
            company_status = "not matching"
    elif len(db_name.split()) == 1 and len(ui_name.split()) > 1:
        # Case 3: db_company_name has only one word and ui_company_name has more than one word
        # Convert the company names by picking the first letter of each word
        ui_company_name_modified = ''.join([word[0] for word in ui_name.split()]).lower()
        db_company_name_modified = db_name.lower()

        # Check whether the modified names are the same
        if ui_company_name_modified == db_company_name_modified:
            print("Case 3: Modified names are equal when converted to lowercase.")
            company_status = "matching"
        else:
            print("Case 3: Modified names are not equal when converted to lowercase.")
            company_status = "not matching"
    else:
        print("No matching conditions found.")
        company_status = "not matching"
    return company_status


# def zoominfo_data(driver, customer_id, linkedin_url):
#     driver.implicitly_wait(120)
#     driver.find_element(By.XPATH,
#                         "//div[text()='Employment History']").is_displayed()
#     time.sleep(2)
#     driver.implicitly_wait(3)
#     company_name_size = len(driver.find_elements(By.XPATH,
#                                                  "//zi-row-group//a[contains(@class,'company-name')]//span"))
#     if company_name_size > 0:
#         company_name = driver.find_element(By.XPATH,
#                                            "//zi-row-group//a[contains(@class,'company-name')]//span").text
#     else:
#         private_size = len(driver.find_elements(By.XPATH, "//zi-company-profile-link//span"))
#         if private_size > 0:
#             company_name = driver.find_element(By.XPATH, "//zi-company-profile-link//span").text
#         else:
#             company_name = None
#     driver.implicitly_wait(3)
#     company_url_size = len(
#         driver.find_elements(By.XPATH, "//zi-row-group//a[contains(@class,'url')]"))
#     if company_url_size > 0:
#         company_url = driver.find_element(By.XPATH,
#                                           "//zi-row-group//a[contains(@class,'url')]").text
#     else:
#         company_url = None
#     driver.implicitly_wait(3)
#     industry_size = len(driver.find_elements(By.XPATH, "//zi-row-group//zi-dotten-text//span"))
#     if industry_size > 0:
#         industry = driver.find_element(By.XPATH, "//zi-row-group//zi-dotten-text//span").text
#     else:
#         industry = None
#     driver.implicitly_wait(3)
#     employess_strength_size = len(
#         driver.find_elements(By.XPATH,
#                              "//zi-row-group//div[contains(@class,'infobox__info')]//span"))
#     if employess_strength_size > 0:
#         employess_strength = driver.find_element(By.XPATH,
#                                                  "//zi-row-group//div[contains(@class,'infobox__info')]//span").text
#         employess_strength = employess_strength.split(":")[1]
#         employess_strength = employess_strength.lstrip()
#         print(employess_strength, " employee strength")
#     else:
#         employess_strength = None
#     driver.implicitly_wait(3)
#     annual_revenue_size = len(driver.find_elements(By.XPATH,
#                                                    "//zi-labelled-infobox[@label='Annual Revenue']//div[contains(@class,'truncate-text')]"))
#     if annual_revenue_size > 0:
#         annual_revenue = driver.find_element(By.XPATH,
#                                              "//zi-labelled-infobox[@label='Annual Revenue']//div[contains(@class,'truncate-text')]").text
#     else:
#         annual_revenue = None
#     title = driver.find_element(By.XPATH, "//div[contains(@class,'contact-details__title')]").text
#     title = title.split(",")[0]
#     zoominfo_url = driver.current_url
#     zoominfo_url = zoominfo_url.split("?")[0]
#     # DirectNumber
#     driver.implicitly_wait(2)
#     direct_number_size = len(driver.find_elements(By.XPATH,
#                                                   "//div[text()='Contact Details']//parent::div//span[text()='Direct']//parent::div//a//span"))
#     if direct_number_size > 0:
#         direct_number = driver.find_element(By.XPATH,
#                                             "//div[text()='Contact Details']//parent::div//span[text()='Direct']//parent::div//a//span").text
#     else:
#         direct_number = None

#     # HqNumber
#     driver.implicitly_wait(2)
#     hq_number_size = len(driver.find_elements(By.XPATH,
#                                               "//div[text()='Contact Details']//parent::div//span[text()='HQ']//parent::div//a//span"))
#     if hq_number_size > 0:
#         hq_number = driver.find_element(By.XPATH,
#                                         "//div[text()='Contact Details']//parent::div//span[text()='HQ']//parent::div//a//span").text
#     else:
#         hq_number = None

#     # MobileNumber
#     driver.implicitly_wait(2)
#     mobile_number_size = len(driver.find_elements(By.XPATH,
#                                                   "//div[text()='Contact Details']//parent::div//span[text()='Mobile']//parent::div//a//span"))

#     if mobile_number_size > 0:
#         mobile_number = driver.find_element(By.XPATH,
#                                             "//div[text()='Contact Details']//parent::div//span[text()='Mobile']//parent::div//a//span").text
#     else:
#         mobile_number = None

#     # BusinessEmail
#     driver.implicitly_wait(2)
#     business_email_size = len(driver.find_elements(By.XPATH,
#                                                    "//div[text()='Contact Details']//parent::div//span[text()='Business']//parent::div//a//span"))
#     if business_email_size > 0:
#         business_email = driver.find_element(By.XPATH,
#                                              "//div[text()='Contact Details']//parent::div//span[text()='Business']//parent::div//a//span").text
#     else:
#         business_email = None

#     # LocalAddress
#     driver.implicitly_wait(2)
#     local_address_size = len(driver.find_elements(By.XPATH,
#                                                   "//div[text()='Location']//parent::div//span[text()='Local']//parent::div//parent::div//span"))
#     if local_address_size > 0:
#         local_address = driver.find_elements(By.XPATH,
#                                              "//div[text()='Location']//parent::div//span[text()='Local']//parent::div//parent::div//span")[
#             -1].text
#         address = local_address.split(",")
#         address_size = len(address)
#         if address_size > 3:
#             country = address[-1]
#             state = address[-2] + address[-3]
#             local_address = address[:-3]
#         elif address_size == 3:
#             country = country = address[-1]
#             state = address[-2]
#             local_address = address[:-2]
#         else:
#             country = address[-1]
#             local_address = address[:-1]
#             state = None
#     else:
#         local_address = None
#         state = None
#         country = None

#     # HQAddress
#     driver.implicitly_wait(2)
#     hq_address_size = len(driver.find_elements(By.XPATH,
#                                                "//div[text()='Location']//parent::div//span[text()='HQ']//parent::div//parent::div//span"))
#     if hq_address_size > 0:
#         hq_address = driver.find_elements(By.XPATH,
#                                           "//div[text()='Location']//parent::div//span[text()='HQ']//parent::div//parent::div//span")[
#             -1].text
#         address = hq_address.split(",")
#         address_size = len(address)
#         if address_size > 3:
#             hq_country = address[-1]
#             hq_state = address[-2] + address[-3]
#             hq_address = address[:-3]
#         elif address_size == 3:
#             hq_country = address[-1]
#             hq_state = address[-2]
#             hq_address = address[:-2]
#         else:
#             hq_country = address[-1]
#             hq_address = address[:-1]
#             hq_state = None
#     else:
#         hq_address = None
#         hq_country = None
#         hq_state = None

#     # Ticker
#     driver.implicitly_wait(3)
#     overview_size = len(driver.find_elements(By.XPATH,
#                                              "//li[contains(@class,'disabled') and contains(@id,'Overview')]"))
#     if overview_size == 0:
#         driver.find_element(By.XPATH, "//span[text()='Overview']").click()
#         time.sleep(2)
#         driver.implicitly_wait(2)
#         ticker_size = len(
#             driver.find_elements(By.XPATH,
#                                  "//zi-text[@data-automation-id='profile-content-ticker']//span"))
#         if ticker_size > 0:
#             ticker = driver.find_element(By.XPATH,
#                                          "//zi-text[@data-automation-id='profile-content-ticker']//span").text
#             ticker_list = ticker.split(":")
#             if len(ticker_list) > 2:
#                 ticker = ticker_list[1] + ":" + ticker_list[2]
#             else:
#                 ticker = ticker_list[1]
#         else:
#             ticker = None
#     else:
#         ticker = None
#     # division
#     division = "global"

#     zoominfo_scraping_url = zoominfo_url
#     zoominfo_scraping_status = 2
#     timestamp = int(datetime.now().timestamp())
#     business_email_status = "unverified"

#     if business_email is None:
#         zoominfo_scraping_status = 4
#         business_email_status = ""

#     customer_info = list(
#         CustomerInfo.objects.filter(customer_id=customer_id).values('customer_name'))
#     company_status = company_comparision(company_name, customer_info[0]['customer_name'])

#     ContactInfo.objects.filter(linkedin_id_url=linkedin_url).update(
#         mobile_number=mobile_number,
#         direct_landline=direct_number,
#         hq_landline=hq_number,
#         location_local=local_address,
#         business_email_id=business_email,
#         country=country,
#         state=state,
#         zoominfo_url=zoominfo_url,
#         zoominfo_scraping_link=zoominfo_scraping_url,
#         zoominfo_scraping_status=zoominfo_scraping_status,
#         be_id_status=business_email_status,
#         last_updated_timestamp=timestamp,
#         company_status=company_status
#     )
    
#     print("contact table insertion done")
#     CustomerInfo.objects.filter(customer_id=customer_id).update(
#         division=division,
#         customer_webpage=company_url,
#         country=hq_country,
#         state=hq_state,
#         location_address=hq_address,
#         number_people=employess_strength,
#         revenue=annual_revenue,
#         industry=industry,
#         ticker=ticker
#     )
#     print("customer table insertion done")

#     #random sleep time
#     time.sleep(random.randint(1*60, 3*60))


# def zoominfo_data(driver, customer_id, linkedin_url, zoominfo_scraping_status):
#     try:
#         driver.implicitly_wait(120)
#         driver.find_element(By.XPATH,
#                             "//div[text()='Employment History']").is_displayed()
#         time.sleep(2)
#         driver.implicitly_wait(3)
#         company_name_size = len(driver.find_elements(By.XPATH,
#                                                      "//zi-row-group//a[contains(@class,'company-name')]//span"))
#         if company_name_size > 0:
#             company_name = driver.find_element(By.XPATH,
#                                                "//zi-row-group//a[contains(@class,'company-name')]//span").text
#         else:
#             private_size = len(driver.find_elements(By.XPATH, "//zi-company-profile-link//span"))
#             if private_size > 0:
#                 company_name = driver.find_element(By.XPATH, "//zi-company-profile-link//span").text
#             else:
#                 company_name = None
#         driver.implicitly_wait(3)
#         company_url_size = len(
#             driver.find_elements(By.XPATH, "//zi-row-group//a[contains(@class,'url')]"))
#         if company_url_size > 0:
#             company_url = driver.find_element(By.XPATH,
#                                               "//zi-row-group//a[contains(@class,'url')]").text
#         else:
#             company_url = None
#         driver.implicitly_wait(3)
#         industry_size = len(driver.find_elements(By.XPATH, "//zi-row-group//zi-dotten-text//span"))
#         if industry_size > 0:
#             industry = driver.find_element(By.XPATH, "//zi-row-group//zi-dotten-text//span").text
#         else:
#             industry = None
#         driver.implicitly_wait(3)
#         employess_strength_size = len(
#             driver.find_elements(By.XPATH,
#                                  "//p[text()='Employees']//following-sibling::p"))
#         if employess_strength_size > 0:
#             employess_strength = driver.find_element(By.XPATH,
#                                                      "//p[text()='Employees']//following-sibling::p").text
#             # employess_strength = employess_strength.split(":")[1]
#             # employess_strength = employess_strength.lstrip()
#             print(employess_strength, " employee strength")
#         else:
#             employess_strength = None
#         driver.implicitly_wait(3)
#         annual_revenue_size = len(driver.find_elements(By.XPATH,
#                                                        "//p[text()='Revenue']//following-sibling::p"))
#         if annual_revenue_size > 0:
#             annual_revenue = driver.find_element(By.XPATH,
#                                                  "//p[text()='Revenue']//following-sibling::p").text
#         else:
#             annual_revenue = None
#         # title = driver.find_element(By.XPATH, "//div[contains(@class,'contact-details__title')]").text
#         # title = title.split(",")[0]
#         zoominfo_url = driver.current_url
#         zoominfo_url = zoominfo_url.split("?")[0]
#         # DirectNumber
#         driver.implicitly_wait(2)
#         direct_number_size = len(driver.find_elements(By.XPATH,
#                                                       "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Phone numbers')]//parent::section//span[contains(text(),'D')]//parent::div//span[@data-automation-id='card-name']"))
#         if direct_number_size > 0:
#             direct_number = driver.find_element(By.XPATH,
#                                                 "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Phone numbers')]//parent::section//span[contains(text(),'D')]//parent::div//span[@data-automation-id='card-name']").text
#         else:
#             direct_number = None

#         # HqNumber
#         driver.implicitly_wait(2)
#         hq_number_size = len(driver.find_elements(By.XPATH,
#                                                   "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Phone numbers')]//parent::section//span[contains(text(),'HQ')]//parent::div//span[@data-automation-id='card-name']"))
#         if hq_number_size > 0:
#             hq_number = driver.find_element(By.XPATH,
#                                             "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Phone numbers')]//parent::section//span[contains(text(),'HQ')]//parent::div//span[@data-automation-id='card-name']").text
#         else:
#             hq_number = None

#         # MobileNumber
#         driver.implicitly_wait(2)
#         mobile_number_size = len(driver.find_elements(By.XPATH,
#                                                       "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Phone numbers')]//parent::section//span[contains(text(),'M')]//parent::div//span[@data-automation-id='card-name']"))

#         if mobile_number_size > 0:
#             mobile_number = driver.find_element(By.XPATH,
#                                                 "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Phone numbers')]//parent::section//span[contains(text(),'M')]//parent::div//span[@data-automation-id='card-name']").text
#         else:
#             mobile_number = None

#         # BusinessEmail
#         driver.implicitly_wait(2)
#         business_email_size = len(driver.find_elements(By.XPATH,
#                                                        "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Emails')]//parent::section//span[@data-automation-id='card-name']"))
#         if business_email_size > 0:
#             business_email = driver.find_element(By.XPATH,
#                                                  "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Emails')]//parent::section//span[@data-automation-id='card-name']").text
#             if len(business_email.strip()) == 0:
#                 business_email = None
#         else:
#             business_email = None

#         # LocalAddress
#         driver.implicitly_wait(2)
#         local_address_size = len(driver.find_elements(By.XPATH,
#                                                       "//h2[text()='Location']//parent::div//div[text()='Local']//following-sibling::div"))
#         if local_address_size > 0:
#             local_address = driver.find_elements(By.XPATH,
#                                                  "//h2[text()='Location']//parent::div//div[text()='Local']//following-sibling::div")[
#                 -1].text
#             address = local_address.split(",")
#             address_size = len(address)
#             if address_size > 3:
#                 country = address[-1]
#                 state = address[-2] + address[-3]
#                 local_address = address[:-3]
#             elif address_size == 3:
#                 country = country = address[-1]
#                 state = address[-2]
#                 local_address = address[:-2]
#             else:
#                 country = address[-1]
#                 local_address = address[:-1]
#                 state = None
#         else:
#             local_address = None
#             state = None
#             country = None

#         # HQAddress
#         driver.implicitly_wait(2)
#         hq_address_size = len(driver.find_elements(By.XPATH,
#                                                    "//h2[text()='Location']//parent::div//div[text()='HQ']//following-sibling::div"))
#         if hq_address_size > 0:
#             hq_address = driver.find_elements(By.XPATH,
#                                               "//h2[text()='Location']//parent::div//div[text()='HQ']//following-sibling::div")[
#                 -1].text
#             address = hq_address.split(",")
#             address_size = len(address)
#             if address_size > 3:
#                 hq_country = address[-1]
#                 hq_state = address[-2] + address[-3]
#                 hq_address = address[:-3]
#             elif address_size == 3:
#                 hq_country = address[-1]
#                 hq_state = address[-2]
#                 hq_address = address[:-2]
#             else:
#                 hq_country = address[-1]
#                 hq_address = address[:-1]
#                 hq_state = None
#         else:
#             hq_address = None
#             hq_country = None
#             hq_state = None

#         # Ticker
#         driver.implicitly_wait(3)
#         overview_size = len(driver.find_elements(By.XPATH,
#                                                  "//li[contains(@class,'disabled') and contains(@id,'Overview')]"))
#         if overview_size == 0:
#             driver.find_element(By.XPATH, "//span[text()='Overview']").click()
#             time.sleep(2)
#             driver.implicitly_wait(2)
#             ticker_size = len(
#                 driver.find_elements(By.XPATH,
#                                      "//zi-text[@data-automation-id='profile-content-ticker']//span"))
#             if ticker_size > 0:
#                 ticker = driver.find_element(By.XPATH,
#                                              "//zi-text[@data-automation-id='profile-content-ticker']//span").text
#                 ticker_list = ticker.split(":")
#                 if len(ticker_list) > 2:
#                     ticker = ticker_list[1] + ":" + ticker_list[2]
#                 else:
#                     ticker = ticker_list[1]
#             else:
#                 ticker = None
#         else:
#             ticker = None
#         # division
#         division = "global"

#         zoominfo_scraping_url = zoominfo_url
#         # zoominfo_scraping_status = 2
#         timestamp = int(datetime.now().timestamp())
#         business_email_status = "unverified"

#         if business_email is None:
#             zoominfo_scraping_status = 4
#             business_email_status = ""

#         customer_info = list(
#             CustomerInfo.objects.filter(customer_id=customer_id).values('customer_name'))
#         company_status = company_comparision(company_name, customer_info[0]['customer_name'])

#         ContactInfo.objects.filter(linkedin_id_url=linkedin_url).update(
#             mobile_number=mobile_number,
#             direct_landline=direct_number,
#             hq_landline=hq_number,
#             location_local=local_address,
#             business_email_id=business_email,
#             country=country,
#             state=state,
#             zoominfo_url=zoominfo_url,
#             zoominfo_scraping_link=zoominfo_scraping_url,
#             zoominfo_scraping_status=zoominfo_scraping_status,
#             be_id_status=business_email_status,
#             last_updated_timestamp=timestamp,
#             company_status=company_status
#         )
#         print("contact table insertion done")
#         CustomerInfo.objects.filter(customer_id=customer_id).update(
#             division=division,
#             customer_webpage=company_url,
#             country=hq_country,
#             state=hq_state,
#             location_address=hq_address,
#             number_people=employess_strength,
#             revenue=annual_revenue,
#             industry=industry,
#             ticker=ticker
#         )
#         print("customer table insertion done")
#         time.sleep(random.randint(1, 10))
#     except Exception as e:
#         logger.info(str(e))
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         print(exc_type, exc_tb.tb_lineno)

def zoominfo_data(driver, customer_id, linkedin_url, zoominfo_scraping_status):
    try:
        driver.implicitly_wait(120)
        driver.find_element(By.XPATH,
                            "//div[text()='Employment History']").is_displayed()
        time.sleep(2)
        driver.implicitly_wait(3)
        company_name_size = len(driver.find_elements(By.XPATH,
                                                     "//zi-row-group//a[contains(@class,'company-name')]//span"))
        if company_name_size > 0:
            company_name = driver.find_element(By.XPATH,
                                               "//zi-row-group//a[contains(@class,'company-name')]//span").text
        else:
            private_size = len(driver.find_elements(By.XPATH, "//zi-company-profile-link//span"))
            if private_size > 0:
                company_name = driver.find_element(By.XPATH, "//zi-company-profile-link//span").text
            else:
                company_name = None
        driver.implicitly_wait(3)
        company_url_size = len(
            driver.find_elements(By.XPATH, "//zi-row-group//a[contains(@class,'url')]"))
        if company_url_size > 0:
            company_url = driver.find_element(By.XPATH,
                                              "//zi-row-group//a[contains(@class,'url')]").text
        else:
            company_url = None
        driver.implicitly_wait(3)
        industry_size = len(driver.find_elements(By.XPATH, "//zi-row-group//zi-dotten-text//span"))
        if industry_size > 0:
            industry = driver.find_element(By.XPATH, "//zi-row-group//zi-dotten-text//span").text
        else:
            industry = None
        driver.implicitly_wait(3)
        employess_strength_size = len(
            driver.find_elements(By.XPATH,
                                 "//p[text()='Employees']//following-sibling::p"))
        if employess_strength_size > 0:
            employess_strength = driver.find_element(By.XPATH,
                                                     "//p[text()='Employees']//following-sibling::p").text
            # employess_strength = employess_strength.split(":")[1]
            # employess_strength = employess_strength.lstrip()
            print(employess_strength, " employee strength")
        else:
            employess_strength = None
        driver.implicitly_wait(3)
        annual_revenue_size = len(driver.find_elements(By.XPATH,
                                                       "//p[text()='Revenue']//following-sibling::p"))
        if annual_revenue_size > 0:
            annual_revenue = driver.find_element(By.XPATH,
                                                 "//p[text()='Revenue']//following-sibling::p").text
        else:
            annual_revenue = None
        # title = driver.find_element(By.XPATH, "//div[contains(@class,'contact-details__title')]").text
        # title = title.split(",")[0]
        zoominfo_url = driver.current_url
        zoominfo_url = zoominfo_url.split("?")[0]
        # DirectNumber
        driver.implicitly_wait(2)
        direct_number_size = len(driver.find_elements(By.XPATH,
                                                      "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Phone numbers')]//parent::section//span[contains(text(),'D')]//parent::div//span[@data-automation-id='card-name']"))
        if direct_number_size > 0:
            direct_number = driver.find_element(By.XPATH,
                                                "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Phone numbers')]//parent::section//span[contains(text(),'D')]//parent::div//span[@data-automation-id='card-name']").text
        else:
            direct_number = None

        # HqNumber
        driver.implicitly_wait(2)
        hq_number_size = len(driver.find_elements(By.XPATH,
                                                  "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Phone numbers')]//parent::section//span[contains(text(),'HQ')]//parent::div//span[@data-automation-id='card-name']"))
        if hq_number_size > 0:
            hq_number = driver.find_element(By.XPATH,
                                            "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Phone numbers')]//parent::section//span[contains(text(),'HQ')]//parent::div//span[@data-automation-id='card-name']").text
        else:
            hq_number = None

        # MobileNumber
        driver.implicitly_wait(2)
        mobile_number_size = len(driver.find_elements(By.XPATH,
                                                      "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Phone numbers')]//parent::section//span[contains(text(),'M')]//parent::div//span[@data-automation-id='card-name']"))

        if mobile_number_size > 0:
            mobile_number = driver.find_element(By.XPATH,
                                                "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Phone numbers')]//parent::section//span[contains(text(),'M')]//parent::div//span[@data-automation-id='card-name']").text
        else:
            mobile_number = None

        # BusinessEmail
        driver.implicitly_wait(2)
        business_email_size = len(driver.find_elements(By.XPATH,
                                                       "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Emails')]//parent::section//span[@data-automation-id='card-name']"))
        if business_email_size > 0:
            business_email = driver.find_element(By.XPATH,
                                                 "//h1[text()='Contact Details']//parent::main//h2[contains(text(),'Emails')]//parent::section//span[@data-automation-id='card-name']").text
            if len(business_email.strip()) == 0:
                business_email = None
        else:
            business_email = None

        # LocalAddress
        driver.implicitly_wait(2)
        local_address_size = len(driver.find_elements(By.XPATH,
                                                      "//h2[text()='Location']//parent::div//div[text()='Local']//following-sibling::div"))
        if local_address_size > 0:
            local_address = driver.find_elements(By.XPATH,
                                                 "//h2[text()='Location']//parent::div//div[text()='Local']//following-sibling::div")[
                -1].text
            address = local_address.split(",")
            address_size = len(address)
            if address_size > 3:
                country = address[-1]
                state = address[-2] + address[-3]
                local_address = address[:-3]
            elif address_size == 3:
                country = country = address[-1]
                state = address[-2]
                local_address = address[:-2]
            else:
                country = address[-1]
                local_address = address[:-1]
                state = None
        else:
            local_address = None
            state = None
            country = None

        # HQAddress
        driver.implicitly_wait(2)
        hq_address_size = len(driver.find_elements(By.XPATH,
                                                   "//h2[text()='Location']//parent::div//div[text()='HQ']//following-sibling::div"))
        if hq_address_size > 0:
            hq_address = driver.find_elements(By.XPATH,
                                              "//h2[text()='Location']//parent::div//div[text()='HQ']//following-sibling::div")[
                -1].text
            address = hq_address.split(",")
            address_size = len(address)
            if address_size > 3:
                hq_country = address[-1]
                hq_state = address[-2] + address[-3]
                hq_address = address[:-3]
            elif address_size == 3:
                hq_country = address[-1]
                hq_state = address[-2]
                hq_address = address[:-2]
            else:
                hq_country = address[-1]
                hq_address = address[:-1]
                hq_state = None
        else:
            hq_address = None
            hq_country = None
            hq_state = None

        # Ticker
        driver.implicitly_wait(3)
        overview_size = len(driver.find_elements(By.XPATH,
                                                 "//li[contains(@class,'disabled') and contains(@id,'Overview')]"))
        if overview_size == 0:
            driver.find_element(By.XPATH, "//span[text()='Overview']").click()
            time.sleep(2)
            driver.implicitly_wait(2)
            ticker_size = len(
                driver.find_elements(By.XPATH,
                                     "//zi-text[@data-automation-id='profile-content-ticker']//span"))
            if ticker_size > 0:
                ticker = driver.find_element(By.XPATH,
                                             "//zi-text[@data-automation-id='profile-content-ticker']//span").text
                ticker_list = ticker.split(":")
                if len(ticker_list) > 2:
                    ticker = ticker_list[1] + ":" + ticker_list[2]
                else:
                    ticker = ticker_list[1]
            else:
                ticker = None
        else:
            ticker = None
        # division
        division = "global"

        zoominfo_scraping_url = zoominfo_url
        # zoominfo_scraping_status = 2
        timestamp = int(datetime.now().timestamp())
        business_email_status = "unverified"

        if business_email is None:
            zoominfo_scraping_status = 4
            business_email_status = ""

        customer_info = list(
            CustomerInfo.objects.filter(customer_id=customer_id).values('customer_name'))
        company_status = company_comparision(company_name, customer_info[0]['customer_name'])

        ContactInfo.objects.filter(linkedin_id_url=linkedin_url).update(
            mobile_number=mobile_number,
            direct_landline=direct_number,
            hq_landline=hq_number,
            location_local=local_address,
            business_email_id=business_email,
            country=country,
            state=state,
            zoominfo_url=zoominfo_url,
            zoominfo_scraping_link=zoominfo_scraping_url,
            zoominfo_scraping_status=zoominfo_scraping_status,
            be_id_status=business_email_status,
            last_updated_timestamp=timestamp,
            company_status=company_status
        )
        print("contact table insertion done")
        CustomerInfo.objects.filter(customer_id=customer_id).update(
            division=division,
            customer_webpage=company_url,
            country=hq_country,
            state=hq_state,
            location_address=hq_address,
            number_people=employess_strength,
            revenue=annual_revenue,
            industry=industry,
            ticker=ticker
        )
        print("customer table insertion done")
        time.sleep(random.randint(1, 10))
    except Exception as e:
        logger.info(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_tb.tb_lineno)


def zerbounce_service():
    print("inside zerobounce")
    zerbounce_flag = False
    last_status = CronJobInfo.objects.filter(model_name='ZERO BOUNCE').order_by('-start_ts').first()
    if last_status==None or last_status.status != 'In Progress':
        zerbounce_flag = True
        job_id = str(uuid.uuid4())
        CronJobInfo.objects.create(
            job_uuid=job_id,
            model_name='ZERO BOUNCE',
            start_ts=int(datetime.now().timestamp()),
            end_ts=None,
            status='In Progress',
            remarks=None
        )

    if zerbounce_flag:
        try:
            data = list(ContactInfo.objects.filter(Q(be_id_status='unverified') & Q(company_status='matching')).values(
                'business_email_id', 'contact_id'))

            print(data)
            if len(data)>0:
                for item in data:
                    business_email = item['business_email_id']
                    contact_id = item['contact_id']
                    print(business_email)
                    print(contact_id)
                    response = requests.get(
                        "https://api.zerobounce.net/v2/validate?api_key=" + api_key + "&email=" + business_email + "&ip_address=")
                    print(response, " reponse get file")
                    business_email_status = 'unverified'
                    if response.status_code == 200:
                        json_data = response.json()
                        print(json_data['status'], " status")
                        business_email_status = json_data['status']
                    timestamp = int(datetime.now().timestamp())
                    # Update email id status in DB
                    ContactInfo.objects.filter(contact_id=contact_id).update(
                        be_id_status=business_email_status,
                        last_updated_timestamp=timestamp
                    )
                    print("udated email id status for the contact : ", contact_id)

                    #randomize every call by 1-10 seconds
                    # time.sleep(random.randint(1, 10))

                print("Job Done successfully")
                CronJobInfo.objects.filter(job_uuid=job_id).update(
                    end_ts=int(datetime.now().timestamp()),
                    status='SUCCESS'
                )
            else:
                print("No data to process")
                CronJobInfo.objects.filter(job_uuid=job_id).update(
                    end_ts=int(datetime.now().timestamp()),
                    status='SUCCESS'
                )

        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            CronJobInfo.objects.filter(job_uuid=job_id).update(
                end_ts=int(datetime.now().timestamp()),
                status='FAILURE',
                remarks=str(e)
            )


def filter_templete_type(message):
    try:
        template_type = "MESSAGE RECEIVED" if "A response" in message else \
            "MESSAGE SENT" if "Sent a message" in message else \
                "CONNECTION ACCEPTED" if "Connection request was accepted" in message else \
                    "CONNECTION REQUESTED" if "Connection request was sent" in message else \
                        "LIKE" if "Liked a post" in message else \
                            "PROFILE VIEWED" if "Viewed profile" in message else \
                                "OTHERS"

        return template_type
    except Exception as e:
        return 'error'


# def dripify_history(driver, campaign_uuid):
#     # options = Options()
#     # # options.add_argument("--headless")
#     # options.add_argument(
#     #     'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
#     # options.add_argument('window-size=1200x600')
#     # driver = webdriver.Chrome(options=options)
#     # driver.maximize_window()
#     # wait = WebDriverWait(driver, 120)
#     # driver.get('https://app.dripify.io/')
#     # time.sleep(1)
#     # # window_handles = driver.window_handles
#     # # second_window_handle = window_handles[1]
#     # # driver.switch_to.window(second_window_handle)
#     # driver.implicitly_wait(180)
#     # driver.find_element(By.ID, "email").is_displayed()
#     # driver.find_element(By.ID, "email").send_keys("lputta@vassarlabs.com")
#     # time.sleep(1)
#     # driver.find_element(By.ID, "password").send_keys("Future@Labs2023")
#     # time.sleep(1)
#     # driver.find_element(By.XPATH, "//button[@type='submit']").is_enabled()
#     # driver.find_element(By.XPATH, "//button[@type='submit']").click()
#     # driver.implicitly_wait(180)
#     # driver.find_element(By.XPATH, "//h2[text()='Statistics']").is_displayed()
#     # time.sleep(2)
#     # print("inside dripify")
#     # driver.find_element(By.ID, "campaigns-link").click()
#     # driver.implicitly_wait(180)
#     # driver.find_element(By.XPATH, "//span[text()='New campaign']//parent::a").is_displayed()
#     # time.sleep(2)
#     # driver.find_element(By.XPATH, "//a[text()=' MFG_USA_Director-Manager-Active-1-5K ']").is_displayed()
#     # time.sleep(2)
#     # driver.find_element(By.XPATH, "//a[text()=' MFG_USA_Director-Manager-Active-1-5K ']").click()
#     # driver.implicitly_wait(180)
#     # driver.find_element(By.XPATH, "//article[@class='leads-pack']").is_displayed()
#     # time.sleep(2)
#     # driver.save_screenshot('error1.png')
#     # all_leads = driver.find_element(By.XPATH,
#     #                                 "//div[contains(text(),' All leads ')]//preceding-sibling::div[@class='campaign-value__main']").text
#     # print(all_leads, " all leads")
#     # completed_leads = driver.find_element(By.XPATH,
#     #                                       "//div[contains(text(),' Completed all steps ')]//preceding-sibling::div[@class='campaign-value__main']").text
#     # print(completed_leads, " completed leads")
#     # leads_xpath_size = len(driver.find_elements(By.XPATH,
#     #                                             "//article[@class='leads-pack']//a[contains(@class,'leads-pack__name leads-pack__name--link')]"))
#     try:
#         # if leads_xpath_size > 0:
#         #     driver.find_element(By.XPATH,
#         #                         "//article[@class='leads-pack']//a[contains(@class,'leads-pack__name leads-pack__name--link')]").click()
#         window_handles = driver.window_handles
#         first_window_handle = window_handles[0]
#         driver.switch_to.window(first_window_handle)
#         print("dripify history  starting")
#         driver.implicitly_wait(120)
#         driver.find_element(By.XPATH, "//button[contains(text(),'Export')]").is_displayed()
#         print("inside export button page")
#         time.sleep(2)
#         driver.find_element(By.XPATH, "//button[@id='leadsView']//parent::div//*[local-name()='svg']").click()
#         time.sleep(1)
#         driver.find_element(By.XPATH, "//button[text()='10']").click()
#         time.sleep(3)
#         spinner_flag = True
#         while spinner_flag:
#             driver.implicitly_wait(1)
#             size_spinner = len(driver.find_elements(By.XPATH, "//div[@class='inline-spinner']"))
#             if size_spinner == 0:
#                 spinner_flag = False

#         total_pages_array = driver.find_elements(By.XPATH,
#                                                  "//ul[@class='pagination']//li[@class='pagination__item']//button")
#         total_papges = total_pages_array[-1].text
#         print(total_papges)
#         # Pages Level
#         for i in range(int(total_papges)):
#             print(i, " ", i + 1)
#             driver.implicitly_wait(20)
#             driver.find_element(By.XPATH,
#                                 "//ul[@class='pagination']//li[contains(@class,'pagination__item')]//button[text()=' " + str(
#                                     i + 1) + " ']").is_displayed()
#             driver.find_element(By.XPATH,
#                                 "//ul[@class='pagination']//li[contains(@class,'pagination__item')]//button[text()=' " + str(
#                                     i + 1) + " ']").click()
#             time.sleep(2)
#             spinner_flag_leads = True
#             while spinner_flag_leads:
#                 driver.implicitly_wait(1)
#                 size_spinner = len(driver.find_elements(By.XPATH, "//div[@class='inline-spinner']"))
#                 if size_spinner == 0:
#                     spinner_flag_leads = False
#             #hk-make a note
#             size_of_leads = len(driver.find_elements(By.XPATH,
#                                                      "//ul[@aria-label='List of leads']//li[@aria-label='Lead']//a"))
#             print(size_of_leads)
#             # Leads level
#             for j in range(int(size_of_leads)):
#                 driver.implicitly_wait(60)
#                 driver.find_elements(By.XPATH, "//ul[@aria-label='List of leads']//li[@aria-label='Lead']//a")[
#                     j].is_displayed()
#                 time.sleep(1)
#                 print(
#                     driver.find_elements(By.XPATH, "//ul[@aria-label='List of leads']//li[@aria-label='Lead']//a")[
#                         j].text, " text name")
#                 if j == 0:
#                     driver.execute_script("arguments[0].scrollIntoView();",
#                                           driver.find_element(By.XPATH, "//div[@class='leads__head']"))

#                 else:
#                     driver.execute_script("arguments[0].scrollIntoView();", driver.find_elements(By.XPATH,
#                                                                                                  "//ul[@aria-label='List of leads']//li[@aria-label='Lead']//a")[
#                         j - 1])

#                 driver.find_elements(By.XPATH, "//ul[@aria-label='List of leads']//li[@aria-label='Lead']//a")[
#                     j].click()
#                 spinner_flag_inside_leads = True
#                 while spinner_flag_inside_leads:
#                     driver.implicitly_wait(1)
#                     size_spinner = len(driver.find_elements(By.XPATH, "//div[@class='inline-spinner']"))
#                     if size_spinner == 0:
#                         spinner_flag_inside_leads = False
#                 time.sleep(1)
#                 driver.implicitly_wait(3)
#                 size_inativity = len(driver.find_elements(By.XPATH, "//div[@class='activity-timeline-empty']"))
#                 linkedin_url = driver.find_element(By.XPATH, "//div[@class='lead-info__avatar']//a").get_attribute(
#                     'href')
#                 print(linkedin_url, " linkedin url")
#                 contact_info = ContactInfo.objects.get(linkedin_url_encrypted=linkedin_url[:-1])
#                 contact_uuid = contact_info.contact_id

#                 if size_inativity == 0:
#                     size_interactions = len(
#                         driver.find_elements(By.XPATH, "//ul[@role='feed']//li[@class='activity-timeline-day']"))
#                     # Go through each interaction
#                     for k in range(size_interactions):
#                         # Get the date when the actions are done
#                         date = driver.find_elements(By.XPATH,
#                                                     "//ul[@role='feed']//li[@class='activity-timeline-day']//h4[contains(@class,'activity-timeline-day__date')]")[
#                             k].text
#                         print(date, " date")
#                         convos_per_day_size = len(driver.find_elements(By.XPATH,
#                                                                        "//ul[@role='feed']//time[contains(text(),'" + date + "')]//ancestor::li[@class='activity-timeline-day']//ul//li"))
#                         # Go through each sub interaction on the same date
#                         for l in range(convos_per_day_size):
#                             # Get the time stamp for each convo
#                             time_stamp = driver.find_elements(By.XPATH,
#                                                               "//ul[@role='feed']//time[contains(text(),'" + date + "')]//ancestor::li[@class='activity-timeline-day']//ul//li//time")[
#                                 l].text
#                             print(time_stamp, " time")
#                             # get the information about the update
#                             message = driver.find_elements(By.XPATH,
#                                                            "//ul[@role='feed']//time[contains(text(),'" + date + "')]//ancestor::li[@class='activity-timeline-day']//ul//li//div")[
#                                 l].text
#                             print(message, " message")

#                             # Assign the Template Type
#                             template_type = filter_templete_type(message)

#                             # convert data, time into time stamp
#                             date_object = datetime.strptime(f"{date},{time_stamp}", "%b %d, %Y,%H:%M")

#                             # Convert to timestamp
#                             timestamp = int(date_object.timestamp())

#                             contact_uuid_instance = ContactInfo(contact_id=contact_uuid)
#                             campaign_id_instance = CampaignInfo(campaign_id=campaign_uuid)
#                             # Check if the touchpoint already exists
#                             existing_touchpoint = LinkedInTouchPoints.objects.filter(
#                                 contact_id=contact_uuid_instance,
#                                 campaign_id=campaign_id_instance,
#                                 date=timestamp
#                             ).exists()

#                             if not existing_touchpoint:
#                                 # Insert Data into LinkedIn Touchpoints table
#                                 LinkedInTouchPoints.objects.create(
#                                     ltp_id=str(uuid.uuid4()),
#                                     tp_type=template_type,
#                                     contact_id=contact_uuid_instance,
#                                     campaign_id=campaign_id_instance,
#                                     date=timestamp,
#                                     subject=message
#                                     # lstatus=request.data['status']
#                                 )

#                     # Go through the mesaaging convo
#                     time.sleep(1)
#                     driver.implicitly_wait(1)
#                     converstation_status = len(driver.find_elements(By.XPATH,
#                                                                     "//main//button[contains(@class,'btn--base btn--to-icon-on-fablet')]"))
#                     if converstation_status == 0:
#                         driver.find_element(By.XPATH, "//main//a[contains(@href,'/inbox')]").click()
#                         driver.implicitly_wait(120)
#                         driver.find_element(By.XPATH,
#                                             "//div[contains(@aria-label,'Outcome message')]").is_displayed()
#                         time.sleep(1)

#                         size_no_of_messages = len(
#                             driver.find_elements(By.XPATH, "//div[@role='feed']//div[contains(@role,'article')]"))
#                         # print(size_no_of_messages, " total no of messages")
#                         last_updated_date = ""
#                         for messages in range(size_no_of_messages):
#                             # Date of the Message
#                             # check date is present or not
#                             driver.implicitly_wait(2)
#                             size_date = len(driver.find_elements(By.XPATH,
#                                                                  "//div[@role='feed']//div[contains(@aria-posinset,'" + str(
#                                                                      messages + 1) + "')]//time[@class='msg__new-day']"))
#                             if size_date > 0:
#                                 date = driver.find_element(By.XPATH,
#                                                            "//div[@role='feed']//div[contains(@aria-posinset,'" + str(
#                                                                messages + 1) + "')]//time[@class='msg__new-day']").text
#                                 last_updated_date = date

#                             # Message
#                             message = driver.find_elements(By.XPATH,
#                                                            "//div[@role='feed']//div[contains(@role,'article')]//div[@class='msg__content']//p")[
#                                 messages].text

#                             # Timestamp
#                             timestamp = driver.find_elements(By.XPATH,
#                                                              "//div[@role='feed']//div[contains(@role,'article')]//div[@class='msg__content']//time")[
#                                 messages].text
#                             time_24hr = datetime.strptime(timestamp, "%I:%M %p").strftime("%H:%M")
#                             print(time_24hr, " time")
#                             # Message Type
#                             type = driver.find_elements(By.XPATH,
#                                                         "//div[@role='feed']//div[contains(@role,'article')]")[
#                                 messages].get_attribute('aria-label')
#                             #
#                             date_object = datetime.strptime(f"{last_updated_date},{time_24hr}", "%a %b %d %Y,%H:%M")

#                             # Convert to timestamp
#                             timestamp_message = int(date_object.timestamp())

#                             # mapping msgs to the above subjects

#                             # Check if the record exists with the specified filter condition
#                             existing_touchpoint = LinkedInTouchPoints.objects.filter(
#                                 contact_id=contact_uuid,
#                                 campaign_id=campaign_uuid,
#                                 date=timestamp_message,
#                                 body=''
#                             ).exists()

#                             if existing_touchpoint:
#                                 LinkedInTouchPoints.objects.filter(contact_id=contact_uuid,
#                                                                    campaign_id=campaign_uuid,
#                                                                    date=timestamp_message).update(
#                                     body=message)

#                             print(type, " message type")
#                             print(last_updated_date, " date")
#                             print(message, " message")
#                             print(timestamp, "  time")

#                         driver.back()
#                         time.sleep(3)
#                     driver.back()
#                     time.sleep(1)
#                     print("------------------------------------------")
#                 else:
#                     print("no update")

#     except Exception as e:
#         driver.save_screenshot('error.png')
#         logger.info(str(e))
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         print(exc_type, exc_tb.tb_lineno)


def apollo_data_fetch():
    apollo_flag = False
    last_status = CronJobInfo.objects.filter(model_name='APOLLO').order_by('-start_ts').first()
    if last_status == None or last_status.status != 'In Progress':
        apollo_flag = True
        job_id = str(uuid.uuid4())
        CronJobInfo.objects.create(
            job_uuid=job_id,
            model_name='APOLLO',
            start_ts=int(datetime.now().timestamp()),
            end_ts=None,
            status='In Progress',
            remarks=None
        )
    else:
        print("in progress so flag is false")
    if apollo_flag:
        try:
            options = Options()
            # options.add_argument("--headless")
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/91.0.4472.124 Safari/537.36')
            options.add_argument('window-size=1200x600')
            driver = webdriver.Chrome(options=options)
            driver.maximize_window()
            wait = WebDriverWait(driver, 120)
            data = list(
                ContactInfo.objects.annotate(customer_name=F('customer_id__customer_name')).filter(
                    (Q(zoominfo_scraping_status__in=[3, 4]) | Q(company_status='not matching')) & Q(
                        apollo_status__isnull=True)).values('linkedin_id_url',
                                                            'customer_id',
                                                            'first_name',
                                                            'last_name',
                                                            'customer_name'))
            print(len(data), " data ")
            driver.implicitly_wait(120)
            if len(data) > 0:
                driver.get('https://app.apollo.io/#/login')
                time.sleep(1)
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

                for entry in data:
                    linkedin_url = entry['linkedin_id_url']
                    customer_id = entry['customer_id']
                    name = entry['first_name'] + " " + entry['last_name']
                    company = entry['customer_name']
                    driver.find_element(By.ID, "side-nav-search").click()
                    driver.implicitly_wait(120)
                    driver.find_element(By.XPATH, "//span[text()='Filters']").is_displayed()
                    time.sleep(2)
                    # driver.find_element(By.XPATH, "//div[text()='More Filters']").click()
                    # time.sleep(2)
                    wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@placeholder="Search People..."]')))
                    # driver.find_element(By.XPATH, "//span[text()='Name']").click()
                    # time.sleep(1)
                    # driver.find_element(By.XPATH,
                    #                     "//span[text()='Name']//ancestor::div[contains(@class,'zp-accordion-header')]//parent::div//input").is_displayed()
                    # driver.find_element(By.XPATH,
                    #                     "//span[text()='Name']//ancestor::div[contains(@class,'zp-accordion-header')]//parent::div//input").clear()
                    input_element = driver.find_element(By.XPATH, '//input[@placeholder="Search People..."]').clear()
                    time.sleep(2)
                    driver.find_element(By.XPATH,
                                        '//input[@placeholder="Search People..."]').send_keys(
                        name)
                    time.sleep(2)
                    driver.find_element(By.XPATH,
                                        '//input[@placeholder="Search People..."]').send_keys(
                        Keys.RETURN)
                    time.sleep(2)
                    print("pressed enter for name")

                    wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Company']")))
                    driver.find_element(By.XPATH, "//span[text()='Company']").click()
                    time.sleep(1)
                    driver.find_element(By.XPATH,
                                        "//span[text()='Company']//ancestor::div[contains(@class,'zp-accordion-header')]//parent::div//following-sibling::input").is_displayed()
                    driver.implicitly_wait(2)
                    size_cross_company = len(driver.find_elements(By.XPATH,
                                                                "//span[text()='Company']//ancestor::div[contains(@class,'zp-accordion-header')]//button[contains(@class,'zp-button')]"))
                    if size_cross_company > 0:
                        driver.find_element(By.XPATH,
                                            "//span[text()='Company']//ancestor::div[contains(@class,'zp-accordion-header')]//button[contains(@class,'zp-button')]").click()
                        time.sleep(1)
                    driver.find_element(By.XPATH,
                                        "//span[text()='Company']//ancestor::div[contains(@class,'zp-accordion-header')]//parent::div//div[contains(text(),'Enter companies')]//following-sibling::input").send_keys(
                        company)
                    time.sleep(2)
                    driver.implicitly_wait(3)
                    driver.find_element(By.XPATH, "//div[contains(@class,'Select-menu-outer')]").is_displayed()
                    time.sleep(1)
                    driver.implicitly_wait(3)
                    size_of_company_name_in_dropdown = len(driver.find_elements(By.XPATH,
                                                                                "//div[contains(@class,'Select-menu-outer')]//div[contains(text(),'" + company + "')]"))
                    if size_of_company_name_in_dropdown > 0:

                        driver.find_element(By.XPATH,
                                            "//div[contains(@class,'Select-menu-outer')]//div[contains(text(),'" + company + "')]").click()
                        print("pressed enter for company")
                        time.sleep(2)
                        driver.implicitly_wait(20)
                        size_results = len(driver.find_elements(By.XPATH, "//table//tbody//tr"))
                        print(size_results, " size")
                        # time.sleep(2)
                        if size_results == 1:
                            name = driver.find_element(By.XPATH, "//table//tbody//tr//td//a").text
                            driver.find_element(By.XPATH, "//table//tbody//tr//td//a").click()
                            print("enterring the user")
                            driver.implicitly_wait(120)
                            driver.find_element(By.XPATH, "//span[text()='Work History']").is_displayed()
                            time.sleep(2)
                            driver.implicitly_wait(3)
                            size_access_number = len(
                                driver.find_elements(By.XPATH,
                                                    "//div[contains(text(),'Access Email & Phone Number')]//parent::button//i"))
                            if size_access_number > 0:
                                driver.find_element(By.XPATH,
                                                    "//div[contains(text(),'Access Email & Phone Number')]//parent::button//i").click()
                                time.sleep(1)

                            # comapny
                            company_name = driver.find_element(By.XPATH,
                                                            "//span[contains(text(),'Current')]//ancestor::small//parent::div//div//div").text
                            # business email
                            driver.implicitly_wait(3)
                            size_business_email = len(
                                driver.find_elements(By.XPATH, "//div[text()='Business']//parent::div//a"))
                            if size_business_email > 0:
                                business_email = driver.find_element(By.XPATH,
                                                                    "//div[text()='Business']//parent::div//a").text
                            else:
                                business_email = None

                            # mobile number primary
                            driver.implicitly_wait(3)
                            size_business_email = len(
                                driver.find_elements(By.XPATH, "//div[text()='Primary']//parent::div//a//span"))
                            if size_business_email > 0:
                                phone_number = driver.find_element(By.XPATH,
                                                                "//div[text()='Primary']//parent::div//a//span").text
                            else:
                                phone_number = None

                            # industry
                            driver.implicitly_wait(3)
                            size_industry = len(
                                driver.find_elements(By.XPATH, "//div[text()='Industry']//parent::div//span"))
                            if size_industry > 0:
                                industry = ""
                                industry_array = driver.find_elements(By.XPATH,
                                                                    "//div[text()='Industry']//parent::div//span")
                                for i in range(len(industry_array)):
                                    industry = industry + industry_array[i].text
                                # industry_list = [element.text for element in industry_array]
                                # industry = "".join(filter(None, industry_list))
                            else:
                                industry = None

                            # company size
                            driver.implicitly_wait(3)
                            size_company_size = len(
                                driver.find_elements(By.XPATH, "//div[text()='Employees']//parent::div//span"))
                            if size_company_size > 0:
                                company_size = driver.find_element(By.XPATH,
                                                                "//div[text()='Employees']//parent::div//span").text
                            else:
                                company_size = None

                            # Annual Revenue
                            driver.implicitly_wait(3)
                            size_annual_revenue = len(
                                driver.find_elements(By.XPATH, "//div[text()='Annual Revenue']//parent::div//div"))
                            if size_annual_revenue == 3:
                                annual_revenue_array = driver.find_elements(By.XPATH,
                                                                            "//div[text()='Annual Revenue']//parent::div//div")
                                annual_revenue = annual_revenue_array[-1].text
                            else:
                                annual_revenue = None

                            print("company name", company_name)
                            print("business email", business_email)
                            print("mobile number", phone_number)
                            print("industry", industry)
                            print("company size", company_size)
                            print("annual revenue", annual_revenue)
                            apollo_status = 1
                            timestamp = int(datetime.now().timestamp())
                            business_email_status = 'unverified'
                            company_status = 'matching'
                            if business_email is None:
                                apollo_status = 3
                                business_email_status = ''

                            # Contact Data updating
                            ContactInfo.objects.filter(linkedin_id_url=linkedin_url).update(
                                business_email_id=business_email,
                                direct_landline=phone_number,
                                apollo_status=apollo_status,
                                last_updated_timestamp=timestamp,
                                be_id_status=business_email_status,
                                company_status=company_status
                            )

                            # Customer data checking
                            cusotmer_data = list(
                                CustomerInfo.objects.filter(customer_id=customer_id).values('industry', 'number_people',
                                                                                            'revenue'))

                            print(cusotmer_data, " customer data")
                            print(len(cusotmer_data[0]['industry']), " ", cusotmer_data[0]['industry'], " industry")

                            # Industry value updation
                            if len(cusotmer_data[0]['industry']) == 0:
                                CustomerInfo.objects.filter(customer_id=customer_id).update(industry=industry)
                                print("updated industry in customer table")

                            # Company Size updation
                            if len(cusotmer_data[0]['number_people']) == 0:
                                CustomerInfo.objects.filter(customer_id=customer_id).update(number_people=company_size)
                                print("updated number of people in customer table")

                            # Annual Revenue Updation
                            if len(cusotmer_data[0]['revenue']) == 0:
                                CustomerInfo.objects.filter(customer_id=customer_id).update(revenue=annual_revenue)
                                print("updated revenue in customer table")

                            

                        else:
                            print("contact not found")
                            apollo_status = 2
                            timestamp = int(datetime.now().timestamp())
                            ContactInfo.objects.filter(linkedin_id_url=linkedin_url).update(
                                apollo_status=apollo_status,
                                last_updated_timestamp=timestamp
                            )
                    else:
                        print("contact not found")
                        apollo_status = 2
                        timestamp = int(datetime.now().timestamp())
                        ContactInfo.objects.filter(linkedin_id_url=linkedin_url).update(
                            apollo_status=apollo_status,
                            last_updated_timestamp=timestamp
                        )

                    #random sleep time

                    # time.sleep(random.randint(1*60, 3*60))
                    

                CronJobInfo.objects.filter(job_uuid=job_id).update(
                    end_ts=int(datetime.now().timestamp()),
                    status='SUCCESS'
                )
                driver.quit()
            else:
                print("No data to process")
                CronJobInfo.objects.filter(job_uuid=job_id).update(
                    end_ts=int(datetime.now().timestamp()),
                    status='SUCCESS'
                )
                driver.quit()

        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            CronJobInfo.objects.filter(job_uuid=job_id).update(
                end_ts=int(datetime.now().timestamp()),
                status='FAILURE',
                remarks=str(e)
            )


def categorized_title(job):
    job_title = {
        'sector vice president': 'VP',
        'evp, chief information, technology and digital officer': 'CIO/CTO/CDO',
        'cio': 'CIO',
        'chief information': 'CIO',
        'chief information officer and director': 'CIO',
        'cto': 'CTO',
        'chief technology': 'CTO',
        'assistant vice president': 'AVP',
        'associate vice president': 'AVP',
        'associate vp': 'AVP',
        'avp': 'AVP',
        'chief digital': 'CDO',
        'cdo': 'CDO',
        'chief marketing & digital officer': 'CDO',
        'senior vice president': 'SVP',
        'senior vp': 'SVP',
        'svp': 'SVP',
        'sr. vice president': 'SVP',
        'head': 'Head',
        'general manager': 'GM',
        'executive vice president': 'EVP',
        'evp': 'EVP',
        'executive/vp,': 'EVP',
        'vice president': 'VP',
        'vp': 'VP',
        'v.p': 'VP',
        'sr. manager': 'Senior Manager',
        'sr manager': 'Senior Manager',
        'senior manager': 'Senior Manager',
        'board member': 'Board Member',
        'manager': 'Manager',
    }
    
    job_lower = job.lower()
    if 'sr' in job_lower or 'senior' in job_lower and 'manager' in job_lower:
        return 'Senior Manager'
    for job_title, role in job_title.items():
        if job_title in job_lower:
            return role
    return 'Unknown'


def categorize_job(job):
    job_lower = job.lower()
    job_categories = {
        'global information technology director': 'Technology',
        'chief ai officer, vp it': 'AI Innovation',
        'digital': 'Digital Transformation',
        'innovation': 'Innovations',
        'innovations': 'Innovations',
        'technology': 'Technology',
        'it': 'Technology',
        'information technology': 'Technology',
        'ai': 'AI Innovation',
        'innovation & transformation': 'Innovation & Digital Transformation',
        'engineering': 'Engineering'
    }
    strategic_roles = ['CIO', 'CTO', 'CIO/CTO/CDO']
    if categorized_title(job) in strategic_roles:
        return 'Strategic'
    for keyword, category in job_categories.items():
        if keyword in job_lower:
            return category

    return 'Technology'


def login_to_gmail():
    print("Login to Gmail")
    username='lila.davis@vassardigital.ai'
    password = 'xcdg ymlx wgyi edgv'
    gmail_host = 'imap.gmail.com'
    gmail_port = 993
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


def check_for_last_n_hours(time_of_last_action):
    # Get the current timestamp as a Unix timestamp in seconds
    # time_of_last_action = datetime.now().timestamp() 
    # time_of_last_action2=int("1705952479736")

    # print(time_of_last_action2,time_of_last_action)
    # Create a datetime object from the current timestamp
    last_action_time = datetime.fromtimestamp(time_of_last_action/1000)

    # Convert the datetime object to the timezone used in your Django settings
    last_action_time = timezone.make_aware(last_action_time)

    # Calculate the current time
    current_time = timezone.now()

    # Calculate the time difference between the current time and the last action time
    time_difference = current_time - last_action_time

    # Check if the time difference is less than 6 hours
    if time_difference.total_seconds() / 3600 < 6:
        return True
    else:
        return False
    

def read_file_locally(campaign_uuid, ui_leads):
    try:
        # file_path = os.getcwd() + '/sales/attachments/Documents/export.csv'
        file_path='/home/vassar/JustGenAIThings/ProjectX64/Backend/indside_sales_backend/InsideSales/sales/attachments/Documents/export.csv'
        print(file_path)
        print("reading data from csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            row_count = len(df)
            final_row_count = row_count - 1
            with transaction.atomic():
                for index, row in df.iterrows():
                    # print(row)
                    contact_uuid = str(uuid.uuid4())
                    linkedin_id_url = row['Linkedin public url']
                    customer_id = str(uuid.uuid4())
                    customer_name = row['Company']
                    Job = str(row['Title'])
                    function = categorize_job(Job)
                    title = categorized_title(Job)


                    # MESSAGE_SENT,1704513088820
                    # time_of_last_action=row['Time of last action']
                    # last_action=row['Last action']
                    
                    # check_for_last_n_hours(time_of_last_action,campaign_uuid,contact_uuid)
                    
                    # Customer Creation
                    try:
                        customer = CustomerInfo.objects.get(customer_name=customer_name)
                        print("Customer already exists with name:", customer_name)
                    except CustomerInfo.DoesNotExist:
                        customer = CustomerInfo.objects.create(
                            customer_id=customer_id,
                            customer_name=customer_name
                        )


                    # Contact Creation
                    if not ContactInfo.objects.filter(linkedin_id_url=linkedin_id_url).exists():
                        print(contact_uuid,customer,row['First name'],row['Last name'],row['Location'],linkedin_id_url,row['LinkedIn email'],title,function,row['Linkedin url'])
                        ContactInfo.objects.create(
                            contact_id=contact_uuid,
                            customer_id=customer,
                            first_name=row['First name'],
                            last_name=row['Last name'],
                            zoominfo_url=contact_uuid,
                            linkedin_id_url=linkedin_id_url,
                            LinkedIn_email=row['LinkedIn email'],
                            title=title,
                            function=function,
                            linkedin_url_encrypted=row['Linkedin url']
                        )

                        print('Data inserted into the database successfully.')
                        # contact and campaign mapping table insertion
                        contact_uuid_instance = ContactInfo(contact_id=contact_uuid)
                        campaign_id_instance = CampaignInfo(campaign_id=campaign_uuid)
                        existing_mapping = CampaignContactMappingInfo.objects.filter(contact_id=contact_uuid_instance,
                                                                                    campaign_id=campaign_id_instance).exists()
                        
                        if not existing_mapping:
                            CampaignContactMappingInfo.objects.create(
                                campaign_contact_mapping_id=str(uuid.uuid4()),
                                contact_id=contact_uuid_instance,
                                campaign_id=campaign_id_instance
                            )

                    else:
                        print("duplicated linkedin_id_url ", linkedin_id_url)

                    

                    # Update the CSV Flag in Campaign table
                    if ui_leads == final_row_count:
                        CampaignInfo.objects.filter(campaign_id=campaign_uuid).update(
                            csv_flag="Completed"
                        )
                    else:
                        camp=CampaignInfo.objects.filter(campaign_id=campaign_uuid).update(
                            csv_flag="In Progress"
                        )
                        
        else:
            print("No such directory exists")
    except Exception as e:

        # driver.save_screenshot('./error.png')
        logger.info(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_tb.tb_lineno)


def open_gmail(driver):
    wait = WebDriverWait(driver, 120)
    driver.execute_script("window.open('https://www.google.com/gmail/about/')")
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


def download_leads_from_gmail(driver):
    time.sleep(5)
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
        "Dripify leads Export")
    print("search")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Search' and @role='button']")))
    driver.find_element(By.XPATH, "//div[text()='Search' and @role='button']").is_enabled()
    driver.find_element(By.XPATH, "//div[text()='Search' and @role='button']").click()
    time.sleep(2)
    driver.save_screenshot("email.png")
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
            # driver.save_screenshot("email1.png")
            date_flag = False
        else:
            time.sleep(5)
            driver.refresh()
            wait.until(
                EC.visibility_of_element_located(
                    (By.XPATH, "//label[text()='Subject']//parent::span//parent::div//input")))
            driver.find_element(By.XPATH, "//label[text()='Subject']//parent::span//parent::div//input").clear()
            driver.find_element(By.XPATH, "//label[text()='Subject']//parent::span//parent::div//input").send_keys(
                "Dripify leads Export")
            print("search")
            wait.until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Search' and @role='button']")))
            driver.find_element(By.XPATH, "//div[text()='Search' and @role='button']").is_enabled()
            driver.find_element(By.XPATH, "//div[text()='Search' and @role='button']").click()

    # driver.save_screenshot("email2.png")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='main']//table//tbody//tr//td[4]")))
    emails = driver.find_elements(By.XPATH, "//div[@role='main']//table//tbody//tr//td[4]")
    emails[0].click()
    time.sleep(3)
    # driver.save_screenshot("email3.png")
    element = driver.find_elements(By.XPATH,
                                   "//span[text()=' One attachment']//parent::span//parent::div//parent::div//span[text()='export.csv']")[
        -1]

    driver.execute_script("arguments[0].scrollIntoView();", element)
    # driver.save_screenshot("email4.png")
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.perform()
    # driver.save_screenshot("email5.png")
    time.sleep(1)
    driver.find_elements(By.XPATH, "//button[contains(@aria-label,'Download attachment')]")[-1].click()
    time.sleep(3)
    file_to_move = 'export.csv'
    downloads_folder = '/home/uttham-it/Downloads/'
    project_directory = os.getcwd()
    new_file_name = 'LeadsFromDripify.csv'
    # Create the full paths for the source and destination
    source_path = os.path.join(downloads_folder, file_to_move)
    destination_path = os.path.join(project_directory, new_file_name)

    shutil.move(source_path, destination_path)
    print(f"File '{file_to_move}' successfully moved to the project directory.")


def login_to_gmail_for_zoominfo():
    
    username='lila.davis@vassardigital.ai'
    password = 'xcdg ymlx wgyi edgv'

    print("Login to Gmail")
    gmail_host_data = 'imap.gmail.com'
    gmail_port_data = 993
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


def fetch_first_two_emails_for_zoominfo(mail):
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


def retrieve_otp_from_email_for_zoominfo():
    # gmail_username='lila.davis@vassardigital.ai'
    # gmail_password = 'xcdg ymlx wgyi edgv'
    
    mail=login_to_gmail_for_zoominfo()
    fetched_data=fetch_first_two_emails_for_zoominfo(mail)
    # print(fetched_data)

    # print(len(fetched_data))
    for i in range(len(fetched_data)):
        body_email=fetched_data[i]['email_body']

        # print(body_email)
        otp = re.findall(r'\b\d{6}\b', body_email)
        # print(otp," otp")
        if otp:
            return otp[0]
    return "No OTP found"
    

# def zoominfo():
#     print("Inside zoominfo")
#     zoominfo_flag = False
#     last_status = CronJobInfo.objects.filter(model_name='ZOOMINFO').order_by('-start_ts').first()
#     if last_status==None or last_status.status != 'In Progress':
#         zoominfo_flag = True
#         job_id = str(uuid.uuid4())
#         CronJobInfo.objects.create(
#             job_uuid=job_id,
#             model_name='ZOOMINFO',
#             start_ts=int(datetime.now().timestamp()),
#             end_ts=None,
#             status='In Progress',
#             remarks=None
#         )
#     else:
#         print("in progress so flag is false")
#     if zoominfo_flag:
#         try:
#             options = Options()
#             # options.add_argument("--headless")
#             options.add_argument(
#                 'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
#             options.add_argument('window-size=1200x600')
#             driver = webdriver.Chrome(options=options)
#             driver.maximize_window()
#             wait = WebDriverWait(driver, 120)
#             data = list(
#                 ContactInfo.objects.annotate(customer_name=F('customer_id__customer_name')).filter(
#                     zoominfo_scraping_status__isnull=True).values('linkedin_id_url',
#                                                                   'customer_id',
#                                                                   'first_name',
#                                                                   'last_name',
#                                                                   'customer_name'))
            
#             driver.implicitly_wait(30)
#             print(len(data), " data")
            
#             if len(data) > 0:
#                 driver.get("https://login.zoominfo.com/")
#                 print("opened zoom info")
#                 time.sleep(2)
#                 driver.find_element(By.ID, 'okta-signin-username').is_displayed()
#                 driver.find_element(By.ID, 'okta-signin-username').send_keys("lila.davis@vassardigital.ai")
#                 driver.find_element(By.ID, "okta-signin-password").send_keys("Future@Labs2024")
#                 time.sleep(2)
#                 driver.find_element(By.XPATH, "//input[@id='okta-signin-submit']").is_enabled()
#                 driver.find_element(By.XPATH, "//input[@id='okta-signin-submit']").click()
#                 time.sleep(20)
#                 code= retrieve_otp_from_email_for_zoominfo()
#                 time.sleep(10)
#                 # print(code)

#                 driver.find_element(By.XPATH, "//input[@id='verify-code-input']").send_keys(code)
#                 print("code entered")
#                 # driver.find_element(By.XPATH, "//input[@id='verify-code-input']").send_keys(code)
#                 # print("code entered")
#                 time.sleep(2)
#                 driver.find_element(By.XPATH, "//button[text()='Verify']").click()
#                 driver.implicitly_wait(120)
#                 driver.find_element(By.XPATH,
#                                     "//button[contains(text(),'Advanced Search')]//parent::div//parent::div//input").is_displayed()
#                 print("inside zoominfo")
#                 driver.implicitly_wait(1)
#                 popup_size = len(driver.find_elements(By.XPATH, "//button[contains(@class,'pendo-close-guide')]"))
#                 if popup_size > 0:
#                     driver.find_element(By.XPATH, "//button[contains(@class,'pendo-close-guide')]").click()
#                     time.sleep(1)

#                 users_not_found = []
#                 zoominfo_scraping_status = None
#                 zoominfo_scraping_url = None

#                 for entry in data:
#                     linkedin_url = entry['linkedin_id_url']
#                     customer_id = entry['customer_id']
#                     name = entry['first_name'] + " " + entry['last_name']
#                     company = entry['customer_name']
#                     print(name, " name ", company, " company")
#                     driver.find_element(By.XPATH,
#                                         "//button[contains(text(),'Advanced Search')]//parent::div//parent::div//input").send_keys(
#                         linkedin_url)
#                     time.sleep(2)
#                     driver.implicitly_wait(10)

#                     contact_flag = len(driver.find_elements(By.XPATH,
#                                                             "//div[@role='listbox']//div[contains(text(),'Contacts')]"))

#                     if contact_flag == 0:
#                         print("no contact")
#                         driver.find_element(By.XPATH, "//button[contains(text(),'Advanced Search')]").click()
#                         time.sleep(3)
#                         driver.implicitly_wait(120)
#                         driver.find_element(By.XPATH, "//button[@data-automation-id='contactName_label']").is_displayed()
#                         driver.execute_script("arguments[0].scrollIntoView(true);", driver.find_element(By.XPATH,
#                                                                                                         "//button[@data-automation-id='contactName_label']"))
#                         time.sleep(2)
#                         driver.find_element(By.XPATH, "//button[@data-automation-id='contactName_label']").click()
#                         time.sleep(1)
#                         driver.implicitly_wait(3)
#                         name_cross_size = len(driver.find_elements(By.XPATH,
#                                                                 "//button[@data-automation-id='contactName_label']//parent::h4//parent::div//i[contains(@class,'exit')]"))
#                         if name_cross_size > 0:
#                             driver.find_element(By.XPATH,
#                                                 "//button[@data-automation-id='contactName_label']//parent::h4//parent::div//i[contains(@class,'exit')]").click()
#                             time.sleep(1)
#                         driver.implicitly_wait(3)
#                         contact_box_size = len(driver.find_elements(By.XPATH,
#                                                                     "//button[@data-automation-id='contactName_label']//parent::h4[contains(@class,'no-chip')]"))
#                         if contact_box_size == 0:
#                             driver.find_element(By.XPATH, "//button[@data-automation-id='contactName_label']").click()
#                             time.sleep(2)
#                         # driver.save_screenshot("error.png")
#                         driver.find_element(By.XPATH, "//input[contains(@id,'fullName')]").clear()
#                         time.sleep(1)
#                         driver.find_element(By.XPATH, "//input[contains(@id,'fullName')]").send_keys(name)
#                         wait.until(EC.element_to_be_clickable(
#                             (By.XPATH, "//input[contains(@id,'fullName')]//parent::div//i[contains(@class,'arrow')]")))
#                         time.sleep(1)
#                         driver.find_element(By.XPATH,
#                                             "//input[contains(@id,'fullName')]//parent::div//i[contains(@class,'arrow')]").is_enabled()
#                         driver.find_element(By.XPATH,
#                                             "//input[contains(@id,'fullName')]//parent::div//i[contains(@class,'arrow')]").click()
#                         time.sleep(2)
#                         driver.find_element(By.XPATH,
#                                             "//button[@data-automation-id='companyNameUrlTicker_label']").is_displayed()
#                         driver.find_element(By.XPATH, "//button[@data-automation-id='companyNameUrlTicker_label']").click()
#                         time.sleep(1)
#                         driver.implicitly_wait(3)

#                         company_cross_size = len(driver.find_elements(By.XPATH,
#                                                                     "//button[@data-automation-id='companyNameUrlTicker_label']//parent::h4//parent::div//i[contains(@class,'exit')]"))
#                         if company_cross_size > 0:
#                             driver.find_element(By.XPATH,
#                                                 "//button[@data-automation-id='companyNameUrlTicker_label']//parent::h4//parent::div//i[contains(@class,'exit')]").click()
#                             time.sleep(1)
#                         driver.implicitly_wait(3)
#                         company_box_size = len(driver.find_elements(By.XPATH,
#                                                                     "//button[@data-automation-id='companyNameUrlTicker_label']//parent::h4[contains(@class,'no-chip')]"))
#                         if company_box_size == 0:
#                             driver.find_element(By.XPATH,
#                                                 "//button[@data-automation-id='companyNameUrlTicker_label']").click()
#                             time.sleep(2)
#                         driver.find_element(By.XPATH,
#                                             "//input[@aria-labelledby='companies_companyNameUrlTicker']").clear()
#                         time.sleep(1)
#                         driver.find_element(By.XPATH,
#                                             "//input[@aria-labelledby='companies_companyNameUrlTicker']").send_keys(company)
#                         wait.until(EC.element_to_be_clickable((By.XPATH,
#                                                             "//input[@aria-labelledby='companies_companyNameUrlTicker']//parent::div//i[contains(@class,'arrow')]")))
#                         time.sleep(1)
#                         driver.find_element(By.XPATH,
#                                             "//input[@aria-labelledby='companies_companyNameUrlTicker']//parent::div//i[contains(@class,'arrow')]").is_enabled()
#                         driver.find_element(By.XPATH,
#                                             "//input[@aria-labelledby='companies_companyNameUrlTicker']//parent::div//i[contains(@class,'arrow')]").click()
#                         time.sleep(2)
#                         driver.implicitly_wait(20)
#                         search_size = len(driver.find_elements(By.XPATH, "//table//tbody//tr//td[2]//a"))
#                         if search_size == 1:
#                             driver.find_element(By.XPATH, "//table//tbody//tr//td[2]//a").click()
#                             zoominfo_data(driver, customer_id, linkedin_url,zoominfo_scraping_status)
#                         else:
#                             print("user not found")
#                             users_not_found.append(linkedin_url + " " + name)
#                             zoominfo_scraping_status = 3
#                             timestamp = int(datetime.now().timestamp())
#                             ContactInfo.objects.filter(linkedin_id_url=linkedin_url).update(
#                                 zoominfo_scraping_status=zoominfo_scraping_status,
#                                 last_updated_timestamp=timestamp
#                             )

#                     else:
#                         print("user found in contacts")
#                         driver.find_element(By.XPATH,
#                                             "//div[@role='listbox']//div[contains(text(),'Contacts')]//parent::div//a").is_displayed()
#                         driver.find_element(By.XPATH,
#                                             "//div[@role='listbox']//div[contains(text(),'Contacts')]//parent::div//a").click()
#                         zoominfo_data(driver, customer_id, linkedin_url,zoominfo_scraping_status)

#                     driver.find_element(By.XPATH,
#                                         "//button[contains(text(),'Advanced Search')]//parent::div//parent::div//input").clear()
#                     print(users_not_found)

#                 CronJobInfo.objects.filter(job_uuid=job_id).update(
#                     end_ts=int(datetime.now().timestamp()),
#                     status='SUCCESS'
#                 )
#                 driver.quit()
#             else:
#                 print("No data to scrape")
#                 CronJobInfo.objects.filter(job_uuid=job_id).update(
#                     end_ts=int(datetime.now().timestamp()),
#                     status='SUCCESS'
#                 )
#                 driver.quit()
                
#         except Exception as e:
#             logger.info(str(e))
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             print(exc_type, exc_tb.tb_lineno)
#             CronJobInfo.objects.filter(job_uuid=job_id).update(
#                 end_ts=int(datetime.now().timestamp()),
#                 status='FAILURE',
#                 remarks=str(e)
#             )

def zoominfo():
    zoominfo_flag = False
    last_status = CronJobInfo.objects.filter(model_name='ZOOMINFO').order_by('-start_ts').first()
    if last_status.status != 'In Progress':
        zoominfo_flag = True
        job_id = str(uuid.uuid4())
        CronJobInfo.objects.create(
            job_uuid=job_id,
            model_name='ZOOMINFO',
            start_ts=int(datetime.now().timestamp()),
            end_ts=None,
            status='In Progress',
            remarks=None
        )
    else:
        print("in progress so flag is false")
    if zoominfo_flag:

        try:
            options = Options()
            # options.add_argument("--headless")
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            options.add_argument('window-size=1200x600')
            driver = webdriver.Chrome(options=options)
            driver.maximize_window()
            wait = WebDriverWait(driver, 120)
            print("opened zoom info")
            data = list(
                ContactInfo.objects.annotate(customer_name=F('customer_id__customer_name')).filter(
                    zoominfo_scraping_status__isnull=True).values('linkedin_id_url',
                                                                  'customer_id',
                                                                  'first_name',
                                                                  'last_name',
                                                                  'customer_name'))
            print(len(data), " data")
            if len(data) > 0:
                driver.get("https://login.zoominfo.com/")
                time.sleep(1)
                print("data to go through zoominfo ", len(data))
                driver.implicitly_wait(30)
                driver.find_element(By.ID, 'okta-signin-username').is_displayed()
                driver.find_element(By.ID, 'okta-signin-username').send_keys("lila.davis@vassardigital.ai")
                driver.find_element(By.ID, "okta-signin-password").send_keys("Future@Labs2024")
                time.sleep(2)
                driver.find_element(By.XPATH, "//input[@id='okta-signin-submit']").is_enabled()
                driver.find_element(By.XPATH, "//input[@id='okta-signin-submit']").click()
                driver.implicitly_wait(60)
                driver.find_element(By.XPATH, "//input[@id='verify-code-input']").is_displayed()
                time.sleep(2)
                # open_gmail(driver)
                code = retrieve_otp_from_email_for_zoominfo()
                driver.find_element(By.XPATH, "//input[@id='verify-code-input']").send_keys(code)
                print("code entered")
                time.sleep(2)
                driver.find_element(By.XPATH, "//button[text()='Verify']").click()
                driver.implicitly_wait(120)
                driver.find_element(By.XPATH,
                                    "//button[contains(text(),'Advanced Search')]//parent::div//parent::div//input").is_displayed()
                print("inside zoominfo")
                driver.implicitly_wait(1)
                popup_size = len(driver.find_elements(By.XPATH, "//button[contains(@class,'pendo-close-guide')]"))
                if popup_size > 0:
                    driver.find_element(By.XPATH, "//button[contains(@class,'pendo-close-guide')]").click()
                    time.sleep(1)

                users_not_found = []
                zoominfo_scraping_status = None
                zoominfo_scraping_url = None

                for entry in data:
                    linkedin_url = entry['linkedin_id_url']
                    customer_id = entry['customer_id']
                    name = entry['first_name'] + " " + entry['last_name']
                    company = entry['customer_name']
                    print(name, " name ", company, " company")
                    driver.find_element(By.XPATH,
                                        "//button[contains(text(),'Advanced Search')]//parent::div//parent::div//input").send_keys(
                        linkedin_url)
                    time.sleep(2)
                    driver.implicitly_wait(10)

                    contact_flag = len(driver.find_elements(By.XPATH,
                                                            "//div[@role='listbox']//div[contains(text(),'Contacts')]"))

                    if contact_flag == 0:
                        print("no contact")
                        driver.find_element(By.XPATH, "//button[contains(text(),'Advanced Search')]").click()
                        time.sleep(3)
                        driver.implicitly_wait(120)
                        driver.find_element(By.XPATH,
                                            "//button[@data-automation-id='contactName_label']").is_displayed()
                        driver.execute_script("arguments[0].scrollIntoView(true);", driver.find_element(By.XPATH,
                                                                                                        "//button[@data-automation-id='contactName_label']"))
                        time.sleep(2)
                        driver.find_element(By.XPATH, "//button[@data-automation-id='contactName_label']").click()
                        time.sleep(1)
                        driver.implicitly_wait(3)
                        name_cross_size = len(driver.find_elements(By.XPATH,
                                                                   "//button[@data-automation-id='contactName_label']//parent::h4//parent::div//i[contains(@class,'exit')]"))
                        if name_cross_size > 0:
                            driver.find_element(By.XPATH,
                                                "//button[@data-automation-id='contactName_label']//parent::h4//parent::div//i[contains(@class,'exit')]").click()
                            time.sleep(1)
                        driver.implicitly_wait(3)
                        contact_box_size = len(driver.find_elements(By.XPATH,
                                                                    "//button[@data-automation-id='contactName_label']//parent::h4[contains(@class,'filter-expanded')]"))
                        if contact_box_size == 0:
                            driver.find_element(By.XPATH, "//button[@data-automation-id='contactName_label']").click()
                            time.sleep(2)
                        # driver.save_screenshot("error.png")
                        driver.find_element(By.XPATH, "//input[contains(@id,'fullName')]").clear()
                        time.sleep(1)
                        driver.find_element(By.XPATH, "//input[contains(@id,'fullName')]").send_keys(name)
                        wait.until(EC.element_to_be_clickable(
                            (By.XPATH, "//input[contains(@id,'fullName')]//parent::div//i[contains(@class,'arrow')]")))
                        time.sleep(1)
                        driver.find_element(By.XPATH,
                                            "//input[contains(@id,'fullName')]//parent::div//i[contains(@class,'arrow')]").is_enabled()
                        driver.find_element(By.XPATH,
                                            "//input[contains(@id,'fullName')]//parent::div//i[contains(@class,'arrow')]").click()
                        time.sleep(2)
                        driver.find_element(By.XPATH,
                                            "//button[@data-automation-id='companyNameUrlTicker_label']").is_displayed()
                        driver.find_element(By.XPATH,
                                            "//button[@data-automation-id='companyNameUrlTicker_label']").click()
                        time.sleep(1)
                        driver.implicitly_wait(3)

                        company_cross_size = len(driver.find_elements(By.XPATH,
                                                                      "//button[@data-automation-id='companyNameUrlTicker_label']//parent::h4//parent::div//i[contains(@class,'exit')]"))
                        if company_cross_size > 0:
                            driver.find_element(By.XPATH,
                                                "//button[@data-automation-id='companyNameUrlTicker_label']//parent::h4//parent::div//i[contains(@class,'exit')]").click()
                            time.sleep(1)
                        driver.implicitly_wait(3)
                        company_box_size = len(driver.find_elements(By.XPATH,
                                                                    "//button[@data-automation-id='companyNameUrlTicker_label']//parent::h4[contains(@class,'filter-expanded')]"))
                        if company_box_size == 0:
                            driver.find_element(By.XPATH,
                                                "//button[@data-automation-id='companyNameUrlTicker_label']").click()
                            time.sleep(2)
                        driver.find_element(By.XPATH,
                                            "//input[@aria-labelledby='companies_companyNameUrlTicker']").clear()
                        time.sleep(1)
                        driver.find_element(By.XPATH,
                                            "//input[@aria-labelledby='companies_companyNameUrlTicker']").send_keys(
                            company)
                        wait.until(EC.element_to_be_clickable((By.XPATH,
                                                               "//input[@aria-labelledby='companies_companyNameUrlTicker']//parent::div//i[contains(@class,'arrow')]")))
                        time.sleep(1)
                        driver.find_element(By.XPATH,
                                            "//input[@aria-labelledby='companies_companyNameUrlTicker']//parent::div//i[contains(@class,'arrow')]").is_enabled()
                        driver.find_element(By.XPATH,
                                            "//input[@aria-labelledby='companies_companyNameUrlTicker']//parent::div//i[contains(@class,'arrow')]").click()
                        time.sleep(2)
                        driver.implicitly_wait(20)
                        search_size = len(driver.find_elements(By.XPATH, "//table//tbody//tr//td[2]//a"))
                        if search_size == 1:
                            driver.find_element(By.XPATH, "//table//tbody//tr//td[2]//a").click()
                            zoominfo_data(driver, customer_id, linkedin_url, "2")
                        else:
                            print("user not found")
                            users_not_found.append(linkedin_url + " " + name)
                            zoominfo_scraping_status = 3
                            timestamp = int(datetime.now().timestamp())
                            ContactInfo.objects.filter(linkedin_id_url=linkedin_url).update(
                                zoominfo_scraping_status=zoominfo_scraping_status,
                                last_updated_timestamp=timestamp
                            )

                    else:
                        print("user found in contacts")
                        driver.find_element(By.XPATH,
                                            "//div[@role='listbox']//div[contains(text(),'Contacts')]//parent::div//a").is_displayed()
                        driver.find_element(By.XPATH,
                                            "//div[@role='listbox']//div[contains(text(),'Contacts')]//parent::div//a").click()
                        zoominfo_data(driver, customer_id, linkedin_url, "1")

                    driver.find_element(By.XPATH,
                                        "//button[contains(text(),'Advanced Search')]//parent::div//parent::div//input").clear()
                    print(users_not_found)

                CronJobInfo.objects.filter(job_uuid=job_id).update(
                    end_ts=int(datetime.now().timestamp()),
                    status='SUCCESS'
                )
                driver.quit()
                # fetching all data
                # data = ContactInfo.objects.select_related('customer_id').all()
                # # Create an array to store JSON objects
                # json_array = []
                # 
                # # Iterate over the queryset and convert each record to a JSON object
                # for contact_info in data:
                #     json_object = {
                #         'linkedin_id_url': contact_info.linkedin_id_url,
                #         'customer_id': contact_info.customer_id.customer_id,
                #         'contact_id': contact_info.contact_id,
                #         'first_name': contact_info.first_name,
                #         'last_name': contact_info.last_name,
                #         'company': contact_info.customer_id.customer_name,
                #         'title': contact_info.title,
                #         'function': contact_info.function,
                #         'linkedin_id_connection': contact_info.linkedin_connected,
                #         'personal_email_id': contact_info.LinkedIn_email,
                #         # 'personal_email_is_status': contact_info.LinkedIn_email_status,
                #         'business_email_id': contact_info.business_email_id,
                #         'business_email_id_status': contact_info.be_id_status,
                #         'mobile_number': contact_info.mobile_number,
                #         'direct_landline': contact_info.direct_landline,
                #         'hq_landline': contact_info.hq_landline,
                #         'country': contact_info.country,
                #         'state': contact_info.state,
                #         'location_local': contact_info.location_local,
                #         'zoominfo_url': contact_info.zoominfo_url,
                #         'zoominfo_scraping_status': contact_info.zoominfo_scraping_status,
                #         'company_status': contact_info.company_status,
                #         'zoominfo_scraping_link': contact_info.zoominfo_scraping_link,
                #         'division': contact_info.customer_id.division,
                #         # 'region': contact_info.customer_id.region,
                #         # 'company_linkedin_page': contact_info.customer_id.customer_linkedin_page,
                #         'company_webpage': contact_info.customer_id.customer_webpage,
                #         'company_country': contact_info.customer_id.country,
                #         'company_state': contact_info.customer_id.state,
                #         'company_address': contact_info.customer_id.location_address,
                #         'number_of_people': contact_info.customer_id.number_people,
                #         'revenue': contact_info.customer_id.revenue,
                #         'industry': contact_info.customer_id.industry,
                #         # 'sub_industry': contact_info.customer_id.sub_industry,
                #         'ticker': contact_info.customer_id.ticker
                #     }
                # 
                #     # Append the JSON object to the array
                #     json_array.append(json_object)
                # print(json_array)
                # # writing into a csv
                # csv_file_name = 'balaji_contacts_output_file.csv'
                # 
                # # Define the CSV header based on the keys in your JSON objects
                # csv_header = [
                #     'linkedin_id_url',
                #     'customer_id',
                #     'contact_id',
                #     'first_name',
                #     'last_name',
                #     'company',
                #     'title',
                #     'function',
                #     'linkedin_id_connection',
                #     'personal_email_id',
                #     'business_email_id',
                #     'business_email_id_status',
                #     'mobile_number',
                #     'direct_landline',
                #     'hq_landline',
                #     'country',
                #     'state',
                #     'location_local',
                #     'zoominfo_url',
                #     'zoominfo_scraping_status',
                #     'company_status',
                #     'division',
                #     'company_webpage',
                #     'company_country',
                #     'company_state',
                #     'company_address',
                #     'number_of_people',
                #     'revenue',
                #     'industry',
                #     'ticker',
                #     'zoominfo_scraping_link'
                # ]
                # 
                # # Write the JSON array to the CSV file
                # with open(csv_file_name, 'w', newline='') as csv_file:
                #     # Create a CSV writer object
                #     csv_writer = csv.DictWriter(csv_file, fieldnames=csv_header)
                # 
                #     # Write the header to the CSV file
                #     csv_writer.writeheader()
                # 
                #     # Write each JSON object as a row in the CSV file
                #     for json_object in json_array:
                #         csv_writer.writerow(json_object)
                # 
                # print(f'CSV file "{csv_file_name}" has been created successfully.')
            else:
                print("No data to process")
                CronJobInfo.objects.filter(job_uuid=job_id).update(
                    end_ts=int(datetime.now().timestamp()),
                    status='SUCCESS'
                )
                driver.quit()

        except Exception as e:
            print("inside if exception")
            zoominfo_scraping_status = 5
            timestamp = int(datetime.now().timestamp())
            print(ContactInfo.objects.filter(linkedin_id_url=linkedin_url))
            try:
                ContactInfo.objects.filter(linkedin_id_url=linkedin_url).update(
                    zoominfo_scraping_status=zoominfo_scraping_status,
                    last_updated_timestamp=timestamp
                )
                CronJobInfo.objects.filter(job_uuid=job_id).update(
                    end_ts=int(datetime.now().timestamp()),
                    status='FAILURE',
                    remarks=str(e)
                )
            except Exception as e:
                print(str(e))


def get_salespersons_and_campaigns():
    salespersons_and_campaigns = {}

    # Assuming you have a ForeignKey relationship between SalesPersonInfo and CampaignInfo
    salespersons = SalesPersonDetails.objects.filter(user_level='User',service='Dripify')
    print(salespersons, "salespersons")

    for salesperson in salespersons:
        campaigns=CampaignSalesPersonMappingInfo.objects.filter(salesperson_id=salesperson.saels_person_id).values('campaign_id')
        # campaigns = salesperson.campaignsalespersonmappinginfo_set.all().select_related('campaign_id')
        salespersons_and_campaigns[salesperson] = campaigns

    print(salespersons_and_campaigns, "salespersons_and_campaigns")
    return salespersons_and_campaigns


def update_dripify_status(campaign_id):
    try:
        pass
        # file_path = os.getcwd() + '/sales/attachments/Documents/export.csv'
        file_path='/home/vassar/JustGenAIThings/ProjectX64/Backend/indside_sales_backend/InsideSales/sales/attachments/Documents/export.csv'
        print(file_path)
        print("reading data from csv for changing dripify status")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            row_count = len(df)
            final_row_count = row_count - 1

            with transaction.atomic():
                for index, row in df.iterrows():
                    # MESSAGE_SENT,1704513088820
                    time_of_last_action=row['Time of last action']
                    linked_url=row['Linkedin public url']
                    print(time_of_last_action,linked_url)

                    

                    if pd.isna(time_of_last_action) or check_for_last_n_hours(time_of_last_action):
                        contacts=ContactInfo.objects.filter(linkedin_id_url=linked_url).values('contact_id')
                        contact=contacts[0]
                        touchpoint=LinkedInTouchPoints.objects.filter(contact_id=contact['contact_id'],campaign_id=campaign_id).exists()
                        if touchpoint:
                            LinkedInTouchPoints.objects.filter(contact_id=contact['contact_id'],campaign_id=campaign_id).update(dripify_status="changed")
                        else:
                            contact_id_instance = ContactInfo(contact_id=contact['contact_id'])
                            campaign_id_instance = CampaignInfo(campaign_id=campaign_id)
                            LinkedInTouchPoints.objects.create(
                               ltp_id=str(uuid.uuid4()),
                               contact_id=contact_id_instance,
                               campaign_id=campaign_id_instance,
                               linkedin_template_id='b1c51066-7a77-4d55-aed5-cc5963f6a24f',
                               date=str(time_of_last_action/1000),
                               dripify_status="changed"
                            )
                        

                    # last_action=row['Last action']
                    # check_for_last_n_hours(time_of_last_action,campaign_id)
                    
                    
    except Exception as e:
        logger.info(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_tb.tb_lineno)

    
def update_campaign_status(campaign_id, driver):
    try:
        campaign = CampaignInfo.objects.filter(campaign_id=campaign_id).values().first()
        print(campaign, "camping in update function")
        print(campaign['campaign_name'], " campaign name")
        driver.save_screenshot(os.getcwd() + '/error.png')
        driver.find_element(By.XPATH, "//a[text()=' " + campaign['campaign_name'] + " ']").is_displayed()
        time.sleep(2)
        driver.find_element(By.XPATH, "//a[text()=' " + campaign['campaign_name'] + " ']").click()
        driver.implicitly_wait(180)
        driver.find_element(By.XPATH, "//article[@class='leads-pack']").is_displayed()
        time.sleep(2)
        driver.save_screenshot('error1.png')
        all_leads = driver.find_element(By.XPATH,
                                        "//div[contains(text(),' All leads ')]//preceding-sibling::div[@class='campaign-value__main']").text
        print(all_leads, " all leads")
        completed_leads = driver.find_element(By.XPATH,
                                              "//div[contains(text(),' Completed all steps ')]//preceding-sibling::div[@class='campaign-value__main']").text
        print(completed_leads, " completed leads")
        leads_xpath_size = len(driver.find_elements(By.XPATH,
                                                    "//article[@class='leads-pack']//a[contains(@class,'leads-pack__name leads-pack__name--link')]"))
        if leads_xpath_size > 0:
            driver.find_element(By.XPATH,
                                "//article[@class='leads-pack']//a[contains(@class,'leads-pack__name leads-pack__name--link')]").click()
            driver.implicitly_wait(120)
            driver.find_element(By.XPATH, "//button[contains(text(),'Export')]").is_displayed()
            print("inside export button page")
            time.sleep(2)
            driver.find_element(By.XPATH, "//button[contains(text(),'Export')]").click()
            driver.implicitly_wait(3)
            size_email_exports = len(driver.find_elements(By.XPATH,
                                                            "//span[contains(text(),'The leads are being exported and will be emailed to you shortly')]"))
            print(size_email_exports, " email size")
            if all_leads == completed_leads:
                CampaignInfo.objects.filter(campaign_id=campaign_id).update(
                    campaign_status='Completed',
                    no_of_leads=all_leads,
                    completed_leads=completed_leads
                )
            else:
                CampaignInfo.objects.filter(campaign_id=campaign_id).update(
                    campaign_status='In Progress',
                    no_of_leads=all_leads,
                    completed_leads=completed_leads
                )

            if size_email_exports > 0:
                time.sleep(120) # Wait for 2 minutes till they send the email
                mail=login_to_gmail()
                fetch_csv(mail)  
                 
            # else:
            #     file_to_move = 'LeadsFromDripify.csv'
            #     downloads_folder = '/home/uttham-it/Downloads/'
            #     project_directory = '/home/uttham-it/work/InsideSales/indside_sales_backend/InsideSales'

            #     # Create the full paths for the source and destination
            #     source_path = os.path.join(downloads_folder, file_to_move)
            #     destination_path = os.path.join(project_directory, file_to_move)

            #     shutil.move(source_path, destination_path)
            #     print(f"File '{file_to_move}' successfully moved to the project directory.")
            
            
            if campaign['csv_flag'] != "Completed":
                read_file_locally(campaign_id, all_leads)
            update_dripify_status(campaign_id)
            # dripify_history(driver, campaign_id)
            # zoominfo(driver)

    except Exception as e:
        driver.save_screenshot('error2.png')
        logger.info(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_tb.tb_lineno)
        return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def automate_salesperson_login(salesperson, driver):
    try:
        # Log in to Dripify
        # driver.get('https://app.dripify.io/')
        # window_handles = driver.window_handles
        # second_window_handle = window_handles[1]
        # driver.switch_to.window(second_window_handle)
        driver.get("https://app.dripify.io/")
        print(salesperson.username, " username")
        print(salesperson.password, " password")
        driver.implicitly_wait(180)
        driver.find_element(By.ID, "email").is_displayed()
        driver.find_element(By.ID, "email").send_keys(salesperson.username)
        time.sleep(1)
        driver.find_element(By.ID, "password").send_keys(salesperson.password)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[@type='submit']").is_enabled()
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        driver.implicitly_wait(180)
        driver.find_element(By.XPATH, "//h2[text()='Statistics']").is_displayed()
        time.sleep(2)
        print("inside dripify")
        # Iterate over campaigns for the salesperson
        campaign_mappings = list(
            CampaignSalesPersonMappingInfo.objects.filter(salesperson_id=salesperson.saels_person_id).values())
        print(campaign_mappings, " mapping of campaisgns")
        
        print("Login done")
        for mapping in campaign_mappings:
            # driver.save_screenshot('error2.png')
            driver.find_element(By.ID, "campaigns-link").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//span[text()='New campaign']//parent::a").is_displayed()
            time.sleep(2)
            campaign = CampaignInfo.objects.filter(campaign_id=mapping['campaign_id_id']).values().first()
            if campaign['campaign_status'] != 'Completed':
                print(f"Processing campaign {campaign['campaign_name']} for {salesperson.username}")
                # Update the campaign status
                update_campaign_status(campaign['campaign_id'], driver)
            else:
                print(f"Skipping completed campaign {campaign.campaign_name} for {salesperson.username}")

    except Exception as e:

        logger.info(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_tb.tb_lineno)
        return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        # Close the browser window
        driver.quit()

#microservice for getting csv file
def dripify():
    print("inside dripify")
    dripify_flag = False
    last_status = CronJobInfo.objects.filter(model_name='DRIPIFY').order_by('-start_ts').first()
    if last_status==None or last_status.status != 'In Progress':
        dripify_flag = True
        job_id = str(uuid.uuid4())
        CronJobInfo.objects.create(
            job_uuid=job_id,
            model_name='DRIPIFY',
            start_ts=int(datetime.now().timestamp()),
            end_ts=None,
            status='In Progress',
            remarks=None
        )
    else:
        print("in progress so flag is false")
    if dripify_flag:
        try:
            salespersons_and_campaigns = get_salespersons_and_campaigns()
            # print(salespersons_and_campaigns, " salespersons and campaigns")
            for salesperson, campaigns in salespersons_and_campaigns.items():
                # try:
                options = Options()
                # options.add_argument("--headless=chrome")
                options.add_argument(
                    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
                options.add_argument('window-size=1200x600')
                options.add_experimental_option("prefs", {
                    "download.default_directory": "/home/vassar/Downloads/",
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "plugins.always_open_pdf_externally": True
                })
                options.add_argument("--disable-popup-blocking")
                driver = webdriver.Chrome(options=options)
                # time.sleep(2)
                driver.maximize_window()
                print(salesperson, " salesperson")
                # open_gmail(driver)
                automate_salesperson_login(salesperson, driver)
                driver.quit()
                # except ObjectDoesNotExist:
                #     print(f"Salesperson {salesperson.salesperson_name} not found in the database.")
                # except Exception as e:
                #     print(f"Error processing salesperson {salesperson.salesperson_name}: {e}")

                time.sleep(5)

            CronJobInfo.objects.filter(job_uuid=job_id).update(
                end_ts=int(datetime.now().timestamp()),
                status='SUCCESS'
            )

            # return Response("success", status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            CronJobInfo.objects.filter(job_uuid=job_id).update(
                end_ts=int(datetime.now().timestamp()),
                status='FAILURE',
                remarks=str(e)
            )

            # return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # time.sleep(3000)


class Campaign(APIView):
    def post(self, request):
        try:
            print("inside campaign creation")

            campaign_type=request.data.get('campaignForm[campaignType]')
            campaign_name=request.data.get('campaignForm[campaignName]')
            dripify_checkbox = request.data.get('campaignForm[dripifyCheckbox]')
            sendgrid_checkbox = request.data.get('campaignForm[campaignType]')
            google_voice_checkbox = request.data.get('campaignForm[campaignType]')
            userid=request.headers.get('Userid')
            dripify_username=""
            dripify_password=""
            campaign_url=""
            timestamp_actual=request.data.get('timeStamp')
            timeStamp = int(int(timestamp_actual) / 1000)  # Convert milliseconds to seconds
            date_of_record = datetime.fromtimestamp(timeStamp).date()
            today_date = date.today()
            
            if date_of_record != today_date:
                campaign_url=request.data.get('campaignForm[campaignName]')
                dripify_template_name=request.data.get('campaignForm[campaignConfig][templateNameDripify]')
                campaign_info = CampaignInfo(
                    campaign_id=str(uuid.uuid4()),
                    campaign_name=campaign_name,
                    campaign_status="Scheduled",
                    created_ts=timestamp_actual,
                    description=campaign_url,
                    attribute_value_pairs=dripify_template_name,
                    no_of_leads=1
                )
                campaign_info.save()
                
                CampaignSalesPersonMappingInfo.objects.create(
                    campaign_salesperson_mapping_id=str(uuid.uuid4()),
                    salesperson_id=userid,
                    campaign_id=campaign_info
                )

                return Response(data={'status':'Success', 'message':"Your campaign will be created on the scheduled date"}, status=status.HTTP_200_OK)


            salespersons = SalesPersonDetails.objects.filter(user_level='User',service='Dripify')

            for salesperson in salespersons:
                if salesperson.saels_person_id == userid:
                    dripify_username=salesperson.username
                    dripify_password=salesperson.password

            if dripify_username=="":
                return Response(data={'status':'Failed', 'message':"No such user found"}, status=status.HTTP_200_OK)
                    
            
            if campaign_type == 'LinkedIn Search':
                campaign_url=request.data.get('campaignForm[campaignSourceUrl]')
                if dripify_checkbox:
                    dripify_template_name=request.data.get('campaignForm[campaignConfig][templateNameDripify]')
                    self.dripify_campaign(dripify_username, dripify_password, campaign_name, campaign_url,campaign_type,userid,dripify_template_name,timestamp_actual)
                if sendgrid_checkbox:
                    self.sendgrid_campaign()
                if google_voice_checkbox:
                    self.google_voice_campaign()
            else:
                file_path = "output_file.csv"
                file_content = request.FILES['campaignForm[campaignSourceCsv]'].read()
                # Write the content to the specified destination
                with open(file_path, 'wb') as destination_file:
                    destination_file.write(file_content)
 
                print(f"File saved successfully at {file_path}")

                if dripify_checkbox:
                    dripify_template_name=request.data.get('campaignForm[campaignConfig][templateNameDripify]')
                    self.dripify_campaign(dripify_username, dripify_password, campaign_name, campaign_url,campaign_type,userid,dripify_template_name,timestamp_actual)
                if sendgrid_checkbox:
                    self.sendgrid_campaign()
                if google_voice_checkbox:
                    self.google_voice_campaign()

            return Response(data={'status':'success','message':"Campaign created Successfully."}, status=status.HTTP_200_OK)


        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Campaign creation Failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def dripify_campaign(self,dripify_username, dripify_password, campaign_name, campaign_url,campaign_type,userid,dripify_template_name,timestamp):
        try:
            # print(request.data['list_name'], " listname")
            options = Options()
            temp_path="//h2[text()='"+dripify_template_name+"']"
            # options.add_argument("--headless")
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            options.add_argument('window-size=1200x600')
            driver = webdriver.Chrome(options=options)
            driver.maximize_window()
            driver.get("https://app.dripify.io/")
            # time.sleep(3000)
            driver.implicitly_wait(180)
            driver.find_element(By.ID, "email").is_displayed()
            driver.find_element(By.ID, "email").send_keys(dripify_username)
            time.sleep(1)
            driver.find_element(By.ID, "password").send_keys(dripify_password)
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[@type='submit']").is_enabled()
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//h2[text()='Statistics']").is_displayed()
            time.sleep(2)
            driver.find_element(By.ID, "campaigns-link").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//span[text()='New campaign']//parent::a").is_displayed()
            time.sleep(2)
            driver.find_element(By.XPATH, "//span[text()='New campaign']//parent::a").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//button[text()=' Add leads ']").is_displayed()
            time.sleep(2)
            driver.find_element(By.XPATH, "//button[text()=' Add leads ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.ID, "leadsPackName").is_displayed()
            time.sleep(1)
            driver.find_element(By.ID, "leadsPackName").send_keys(campaign_name)
            file_path = "output_file.csv"

            if campaign_type == 'Upload CSV File':
                driver.find_element(By.XPATH, "//a[text()='Upload CSV file']").click()
                driver.implicitly_wait(180)
                driver.find_element(By.XPATH, "//input[@type='file']").is_displayed()
                time.sleep(2)
                driver.find_element(By.XPATH, "//input[@type='file']").send_keys(
                    os.getcwd() + "/output_file.csv")
            else:
                driver.find_element(By.ID, "LinkedInSearch").send_keys(campaign_url)
                time.sleep(15)
                # time.sleep(2)
                driver.find_element(By.XPATH, "//input[@type='checkbox']").click()
            time.sleep(2)
            
            no_of_profiles_found = driver.find_element(By.XPATH, "//p[text()=' LinkedIn profiles found: ']//b").text
            print(no_of_profiles_found, " profiles found")
            driver.find_element(By.XPATH, "//button[text()=' Create a list ']").is_enabled()
            driver.find_element(By.XPATH, "//button[text()=' Create a list ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//button[text()=' Next ']").is_displayed()
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[text()=' Next ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//button[text()=' Saved Templates ']").is_displayed()
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[text()=' Saved Templates ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, temp_path).is_displayed()
            time.sleep(1)
            driver.find_element(By.XPATH, temp_path).click()
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[text()=' Select template ']").is_enabled()
            driver.find_element(By.XPATH, "//button[text()=' Select template ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//button[text()=' Next ']").is_displayed()
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[text()=' Next ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.ID, "Name").is_displayed()
            driver.find_element(By.ID, "Name").send_keys(campaign_name)
            time.sleep(2)
            driver.find_element(By.ID, "saveCampaignBtn").is_enabled()
            driver.find_element(By.ID, "saveCampaignBtn").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//a[text()=' Back to campaigns ']").is_displayed()
            time.sleep(1)
            driver.find_element(By.XPATH, "//a[text()=' Back to campaigns ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//a[text()=' " + campaign_name + " ']").is_displayed()
            time.sleep(2)
            campaign_creation_status = "Created"
            campaign_id = str(uuid.uuid4())
            driver.quit()
            no_of_profiles_found="300"
            print(campaign_id,
                campaign_name,
                campaign_creation_status,
                timestamp,
                no_of_profiles_found)
            
            campaign_info = CampaignInfo(
                campaign_id=campaign_id,
                campaign_name=campaign_name,
                campaign_status=campaign_creation_status,
                created_ts=timestamp,
                no_of_leads=no_of_profiles_found
            )
            campaign_info.save()
            time.sleep(2)
            campaign_creation_status = "success"

            CampaignSalesPersonMappingInfo.objects.create(
                campaign_salesperson_mapping_id=str(uuid.uuid4()),
                salesperson_id=userid,
                campaign_id=campaign_info
            )


            json_array = []
            json_object = {
                'campaign_name': campaign_name,
                'campaign_status': campaign_creation_status,
                'created_ts': timestamp,
                "no_of_users": no_of_profiles_found
            }


            json_array.append(json_object)
            campaign_creation_status = "success"
            return Response(json_array, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def sendgrid_campaign(self):
        pass
    
    def google_voice_campaign(self):
        pass
    
    def dk(self, request):
        print(request.headers, " request")
        try:
            campaign_info = CampaignSalesPersonMappingInfo.objects.filter(
                salesperson_id=request.headers['Userid']
            ).values('campaign_id__campaign_name', 'campaign_id__no_of_users', 'campaign_id__created_ts',
                     'campaign_id__campaign_status')
            print(campaign_info, " campaign info")
            json_array = []
            for data in campaign_info:
                json_object = {
                    'campaign_name': data['campaign_id__campaign_name'],
                    'no_of_users': data['campaign_id__no_of_users'],
                    'created_date': data['campaign_id__created_ts'],
                    'campaign_status': data['campaign_id__campaign_status']
                }
                json_array.append(json_object)
            return Response(json_array, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            zoominfo()
            return Response("success", status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DataView(APIView):

    def get(self, request, *args, **kwargs):
        try:

            data = ContactInfo.objects.select_related('customer_id').all()
            # Create an array to store JSON objects
            json_array = []

            # Iterate over the queryset and convert each record to a JSON object
            for contact_info in data:
                json_object = {
                    'linkedin_id_url': contact_info.linkedin_id_url,
                    'customer_id': contact_info.customer_id.customer_id,
                    'contact_id': contact_info.contact_id,
                    'first_name': contact_info.first_name,
                    'last_name': contact_info.last_name,
                    'company': contact_info.customer_id.customer_name,
                    'title': contact_info.title,
                    'function': contact_info.function,
                    'linkedin_id_connection': contact_info.linkedin_connected,
                    'personal_email_id': contact_info.LinkedIn_email,
                    # 'personal_email_is_status': contact_info.LinkedIn_email_status,
                    'business_email_id': contact_info.business_email_id,
                    'business_email_id_status': contact_info.be_id_status,
                    'mobile_number': contact_info.mobile_number,
                    'direct_landline': contact_info.direct_landline,
                    'hq_landline': contact_info.hq_landline,
                    'country': contact_info.country,
                    'state': contact_info.state,
                    'location_local': contact_info.location_local,
                    'zoominfo_url': contact_info.zoominfo_url,
                    'zoominfo_scraping_status': contact_info.zoominfo_scraping_status,
                    'company_status': contact_info.company_status,
                    # 'zoominfo_scraping_link': contact_info.zoominfo_scraping_link,
                    'division': contact_info.customer_id.division,
                    # 'region': contact_info.customer_id.region,
                    # 'company_linkedin_page': contact_info.customer_id.customer_linkedin_page,
                    'company_webpage': contact_info.customer_id.customer_webpage,
                    'company_country': contact_info.customer_id.country,
                    'company_state': contact_info.customer_id.state,
                    'company_address': contact_info.customer_id.location_address,
                    'number_of_people': contact_info.customer_id.number_people,
                    'revenue': contact_info.customer_id.revenue,
                    'industry': contact_info.customer_id.industry,
                    # 'sub_industry': contact_info.customer_id.sub_industry,
                    'ticker': contact_info.customer_id.ticker
                }

                # Append the JSON object to the array
                json_array.append(json_object)

            # Convert the array to a JSON-formatted string
            # json_data = json.dumps(json_array, indent=2)

            # Print or return the JSON-formatted string
            print(json_array)
            return Response(json_array, status=status.HTTP_200_OK)

        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        print(request.data, " post request")
        try:
            db_email_list = list(
                ContactInfo.objects.filter(contact_id=request.data['contact_id']).values('business_email_id'))
            print(db_email_list, " db email")
            db_email = db_email_list[0]['business_email_id']
            business_email_status = "unverified"
            if db_email == request.data['business_email_id']:
                print("matched")
            else:
                print("mismatch lets update the status")
                response = requests.get(
                    "https://api.zerobounce.net/v2/validate?api_key=" + api_key + "&email=" + request.data[
                        'business_email_id'] + "&ip_address=")
                print(response, " reponse get file")
                if response.status_code == 200:
                    json_data = response.json()
                    print(json_data['status'], " status")
                    business_email_status = json_data['status']

            ContactInfo.objects.filter(contact_id=request.data['contact_id']).update(
                first_name=request.data['first_name'],
                last_name=request.data['last_name'],
                title=request.data['title'],
                function=request.data['function'],
                linkedin_id_url=request.data['linkedin_id_url'],
                linkedin_connected=request.data['linkedin_id_connection'],
                LinkedIn_email=request.data['personal_email_id'],
                business_email_id=request.data['business_email_id'],
                be_id_status=business_email_status,
                mobile_number=request.data['mobile_number'],
                direct_landline=request.data['direct_landline'],
                hq_landline=request.data['hq_landline'],
                location_local=request.data['location_local'],
                country=request.data['country'],
                state=request.data['state'],
                zoominfo_url=request.data['zoominfo_url'],
                zoominfo_scraping_status=request.data['zoominfo_scraping_status'],
                company_status=request.data['company_status']
            )
            CustomerInfo.objects.filter(customer_id=request.data['customer_id']).update(
                customer_name=request.data['company'],
                division=request.data['division'],
                customer_webpage=request.data['company_webpage'],
                country=request.data['company_country'],
                state=request.data['company_state'],
                location_address=request.data['company_address'],
                number_people=request.data['number_of_people'],
                revenue=request.data['revenue'],
                industry=request.data['industry'],
                ticker=request.data['ticker']
            )

            # print(request.data, " request")
            return Response("Success", status=status.HTTP_200_OK)

        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LinkedInActivities(APIView):
    def post(self, request):

        try:

            linkedin_template_id = str(uuid.uuid4())
            LinkedInTemplate.objects.create(
                linkedin_template_id=linkedin_template_id,
                template_type=request.data['type'],
                body=request.data['body']
            )
            contact_id_instance = ContactInfo(contact_id=request.data['contact_id'])
            campaign_id_instance = CampaignInfo(campaign_id=request.data['campaign_id'])
            linkedin_template_id_instance = LinkedInTemplate(linkedin_template_id=linkedin_template_id)
            timestamp = datetime.now().strftime('%m-%d-%Y %H:%M:%S')

            LinkedInTouchPoints.objects.create(
                ltp_id=str(uuid.uuid4()),
                contact_id=contact_id_instance,
                campaign_id=campaign_id_instance,
                linkedin_template_id=linkedin_template_id_instance,
                date=timestamp,
                lstatus=request.data['status']
            )

            # print(request.data, " request")
            return Response("Success", status=status.HTTP_200_OK)

        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, id):
        print(request)
        try:
            touchpoints_data = LinkedInTouchPoints.objects.filter(contact_id=id).values(
                'lstatus',
                'date')
            template_data = LinkedInTemplate.objects.filter(
                linkedintouchpoints__contact_id=id).values(
                'template_type', 'body')
            json_array = []
            for touchpoint, template in zip(touchpoints_data, template_data):
                json_object = {
                    "linkedIn_status": touchpoint['lstatus'],
                    "date": touchpoint['date'],
                    "template_type": template['template_type'],
                    "body": template['body']
                }
                json_array.append(json_object)

            print(touchpoints_data, " touchpoint data")
            print(template_data, " template data")

            return Response(json_array, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailActivities(APIView):
    def post(self, request):

        try:

            email_template_id = str(uuid.uuid4())
            EmailTemplate.objects.create(
                etemplate_id=email_template_id,
                subject=request.data['subject'],
                body=request.data['body']
            )
            contact_id_instance = ContactInfo(contact_id=request.data['contact_id'])
            campaign_id_instance = CampaignInfo(campaign_id=request.data['campaign_id'])
            email_template_id_instance = EmailTemplate(etemplate_id=email_template_id)
            timestamp = datetime.now().strftime('%m-%d-%Y %H:%M:%S')

            EmailTouchPoints.objects.create(
                etouchpoint_id=str(uuid.uuid4()),
                contact_id=contact_id_instance,
                campaign_id=campaign_id_instance,
                etemplate_id=email_template_id_instance,
                date=timestamp,
                estatus=request.data['status'],
                etype="Business"
            )

            # print(request.data, " request")
            return Response("Success", status=status.HTTP_200_OK)

        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, id):
        try:
            touchpoints_data = EmailTouchPoints.objects.filter(contact_id=id).values(
                'estatus',
                'date')
            template_data = EmailTemplate.objects.filter(
                emailtouchpoints__contact_id=id).values(
                'subject', 'body')
            json_array = []
            for touchpoint, template in zip(touchpoints_data, template_data):
                json_object = {
                    "email_status": touchpoint['estatus'],
                    "date": touchpoint['date'],
                    "subject": template['subject'],
                    "body": template['body']
                }
                json_array.append(json_object)

            print(touchpoints_data, " touchpoint data")
            print(template_data, " template data")

            return Response(json_array, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PhoneActivities(APIView):
    def post(self, request):

        try:
            contact_id_instance = ContactInfo(contact_id=request.data['contact_id'])
            campaign_id_instance = CampaignInfo(campaign_id=request.data['campaign_id'])
            timestamp = datetime.now().strftime('%m-%d-%Y %H:%M:%S')

            PhoneTouchPoints.objects.create(
                ptp_id=str(uuid.uuid4()),
                contact_id=contact_id_instance,
                campaign_id=campaign_id_instance,
                date=timestamp,
                start_time=request.data['start_time'],
                end_time=request.data['end_time'],
                subject=request.data['subject'],
                description=request.data['description']
                # pstatus=request.data['status'],
            )

            return Response("Success", status=status.HTTP_200_OK)

        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, id):
        try:
            touchpoints_data = PhoneTouchPoints.objects.filter(contact_id=id).values(
                'start_time',
                'end_time',
                'subject',
                'description',
                'date')
            # template_data = EmailTemplate.objects.filter(
            #     emailtouchpoints__contact_id=request.data['contact_id']).values(
            #     'subject', 'body')
            json_array = []
            for touchpoint in touchpoints_data:
                json_object = {
                    "start_time": touchpoint['start_time'],
                    "date": touchpoint['date'],
                    "subject": touchpoint['subject'],
                    "end_time": touchpoint['end_time'],
                    "description": touchpoint['description']
                }
                json_array.append(json_object)

            print(touchpoints_data, " touchpoint data")
            # print(template_data, " template data")

            return Response(json_array, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#for user and admin
class CampaignList(APIView):
    serializer = PhoneTouchPointsSerializer(PhoneTouchPointsSerializer, many=True)
    serializer_linkedin = LinkedInTouchPointsSerializer(LinkedInTouchPointsSerializer, many=True)
    serializer_email = EmailTouchPointsSerializer(EmailTouchPointsSerializer, many=True)
    def get(self, request):
        try:
            user_type=request.headers['Scope']
            if user_type=="User":
                userId = request.headers['Userid']
                print(userId)
                final_arr=[]
                # Get all campaigns
                campaigns = CampaignSalesPersonMappingInfo.objects.filter(salesperson_id=userId).values('campaign_id')
                for campaign in campaigns:
                    campaigns_list = list(CampaignInfo.objects.filter(campaign_id=campaign['campaign_id']).values())

                    # final_arr=[]
                    for campaign in campaigns_list:
                        
                        #emails touchpoints
                        email_touchpoint_data = EmailTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_email=EmailTouchPointsSerializer(email_touchpoint_data, many=True)
                        count_emails=0
                        # print(serializer_email.data)
                        map={}
                        count_completed_email=0
                        delivered=0
                        unsubscribe=0
                        responded=0
                        meetingsSetup=0

                        for touchpoint in serializer_email.data:
                            if touchpoint.get('contact_id') not in map:
                                if touchpoint.get('estatus')=="Completed":    
                                    map[touchpoint.get('contact_id')]="Completed"
                                else:
                                    map[touchpoint.get('contact_id')]="Not Completed"
                            elif touchpoint.get('estatus')=="Completed":
                                map[touchpoint.get('contact_id')]="Completed"

                            if touchpoint.get('etype')=="DELIVERED":
                                delivered+=1
                            if touchpoint.get('etype')=="UNSUBSCRIBED":
                                unsubscribe+=1   
                            if touchpoint.get('etype')=="RESPONDED":
                                responded+=1
                            if touchpoint.get('etype')=="MEETINGS":
                                meetingsSetup+=1 

                        for (key,value) in map.items():
                            if value=="Completed":
                                count_completed_email+=1
                            count_emails+=1          
                        
                        #linkedIn touchpoints
                        linkedin_touchpoint_data = LinkedInTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_linkedin=LinkedInTouchPointsSerializer(linkedin_touchpoint_data, many=True)
                        count_linkedinmessages=0
                        map_linkedin={}
                        count_completed_linkedin=0
                        connection_request=0
                        inmail_responded=0
                        meetingsSetup_linkedin=0
                        

                        for touchpoint in serializer_linkedin.data:
                            if touchpoint.get('contact_id') not in map:
                                if touchpoint.get('lstatus')=="Completed":    
                                    map_linkedin[touchpoint.get('contact_id')]="Completed"
                                else:
                                    map_linkedin[touchpoint.get('contact_id')]="Not Completed"
                            elif touchpoint.get('lstatus')=="Completed":
                                map_linkedin[touchpoint.get('contact_id')]="Completed"

                            if touchpoint.get('tp_type')=="CONNECTION REQUEST SENT":
                                connection_request+=1
                            if touchpoint.get('tp_type')=="INMAIL SENT":
                                inmail_responded+=1   
                            if touchpoint.get('tp_type')=="MEETING SCHEDULED":
                                meetingsSetup_linkedin+=1
                            

                        for (key,value) in map_linkedin.items():
                            if value=="Completed":
                                count_completed_linkedin+=1
                            count_linkedinmessages+=1  
                        
                        #calls touchpoints
                        phone_touchpoint_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer=PhoneTouchPointsSerializer(phone_touchpoint_data, many=True)
                        count_call=0
                        map_calls={}
                        count_completed_call=0
                        connected=0
                        removed=0
                        meetingsSetup_calls=0
                        

                        for touchpoint in serializer.data:
                            if touchpoint.get('contact_id') not in map_calls:
                                if touchpoint.get('pstatus')=="Completed":    
                                    map_calls[touchpoint.get('contact_id')]="Completed"
                                else:
                                    map_calls[touchpoint.get('contact_id')]="Not Completed"
                            elif touchpoint.get('pstatus')=="Completed":
                                map_calls[touchpoint.get('contact_id')]="Completed"

                            if touchpoint.get('pstatus')=="CONNECTED":
                                connected+=1
                            if touchpoint.get('pstatus')=="REMOVED":
                                removed+=1   
                            if touchpoint.get('pstatus')=="MEETING SCHEDULED":
                                meetingsSetup_calls+=1
                            

                        for (key,value) in map_calls.items():
                            if value=="Completed":
                                count_completed_call+=1
                            count_call+=1 

                                
                        
                        json={
                            "campaignId":campaign["campaign_id"],
                            "campaignStatus":campaign["campaign_status"],
                            "campaignName":campaign["campaign_name"],
                            "createdDate":campaign["created_ts"],
                            "leads":campaign["no_of_leads"],
                            "campaignStartedLinkedIn":round((float(count_linkedinmessages)/float(campaign["no_of_leads"]))*100,2),
                            "campaignStartedCalls":round((float(meetingsSetup_calls)/float(campaign["no_of_leads"]))*100,2),
                            "campaignStartedEmail":round((float(count_emails)/float(campaign["no_of_leads"]))*100,2),
                            "campaignActive":campaign["campaign_status"]=='In Progress',
                            "linkedIn":{
                                "campaignStarted":count_linkedinmessages,
                                "campaignCompleted":count_completed_linkedin,
                                "acceptedConnectionRequest":connection_request,
                                "respondedToInMail":inmail_responded,
                                "meetingsSetup":meetingsSetup_linkedin,
                            },
                            "calls":{
                                "campaignStarted":count_call,
                                "campaignCompleted":count_completed_call,
                                "connected":connected,
                                "removedFromList":removed,
                                "meetingsSetup":meetingsSetup_calls,
                            },
                            "emails":{
                                "campaignStarted":count_emails,
                                "campaignCompleted":count_completed_email,
                                "delivered":delivered,
                                "unsubscribe":unsubscribe,
                                "responded":responded,
                                "meetingsSetup":meetingsSetup,
                            }
                        }

                        final_arr.append(json)
                # print(final_arr)
                return Response({"status":"Success","json":final_arr}, status=status.HTTP_200_OK)
            elif user_type=="Admin":
                # userId = request.headers['Userid']
                # print(userId)
                salespersons=SalesPersonInfo.objects.all().values('salesperson_id','salesperson_name')
                # final_arr=[]
                final_sales_data=[]
                for salesperson in salespersons:
                    # Get all campaigns
                    final_arr=[]
                    userId=salesperson['salesperson_id']
                    campaigns = CampaignSalesPersonMappingInfo.objects.filter(salesperson_id=userId).values('campaign_id')
                    for campaign in campaigns:
                        campaigns_list = list(CampaignInfo.objects.filter(campaign_id=campaign['campaign_id']).values())

                        # final_arr=[]
                        for campaign in campaigns_list:
                            
                            #emails touchpoints
                            email_touchpoint_data = EmailTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                            serializer_email=EmailTouchPointsSerializer(email_touchpoint_data, many=True)
                            count_emails=0
                            # print(serializer_email.data)
                            map={}
                            count_completed_email=0
                            delivered=0
                            unsubscribe=0
                            responded=0
                            meetingsSetup=0

                            for touchpoint in serializer_email.data:
                                if touchpoint.get('contact_id') not in map:
                                    if touchpoint.get('estatus')=="Completed":    
                                        map[touchpoint.get('contact_id')]="Completed"
                                    else:
                                        map[touchpoint.get('contact_id')]="Not Completed"
                                elif touchpoint.get('estatus')=="Completed":
                                    map[touchpoint.get('contact_id')]="Completed"

                                if touchpoint.get('etype')=="DELIVERED":
                                    delivered+=1
                                if touchpoint.get('etype')=="UNSUBSCRIBED":
                                    unsubscribe+=1   
                                if touchpoint.get('etype')=="RESPONDED":
                                    responded+=1
                                if touchpoint.get('etype')=="MEETINGS":
                                    meetingsSetup+=1 

                            for (key,value) in map.items():
                                if value=="Completed":
                                    count_completed_email+=1
                                count_emails+=1          
                            
                            #linkedIn touchpoints
                            linkedin_touchpoint_data = LinkedInTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                            serializer_linkedin=LinkedInTouchPointsSerializer(linkedin_touchpoint_data, many=True)
                            count_linkedinmessages=0
                            map_linkedin={}
                            count_completed_linkedin=0
                            connection_request=0
                            inmail_responded=0
                            meetingsSetup_linkedin=0
                            

                            for touchpoint in serializer_linkedin.data:
                                if touchpoint.get('contact_id') not in map:
                                    if touchpoint.get('lstatus')=="Completed":    
                                        map_linkedin[touchpoint.get('contact_id')]="Completed"
                                    else:
                                        map_linkedin[touchpoint.get('contact_id')]="Not Completed"
                                elif touchpoint.get('lstatus')=="Completed":
                                    map_linkedin[touchpoint.get('contact_id')]="Completed"

                                if touchpoint.get('tp_type')=="CONNECTION REQUEST SENT":
                                    connection_request+=1
                                if touchpoint.get('tp_type')=="INMAIL SENT":
                                    inmail_responded+=1   
                                if touchpoint.get('tp_type')=="MEETING SCHEDULED":
                                    meetingsSetup_linkedin+=1
                                

                            for (key,value) in map_linkedin.items():
                                if value=="Completed":
                                    count_completed_linkedin+=1
                                count_linkedinmessages+=1  
                            
                            #calls touchpoints
                            phone_touchpoint_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                            serializer=PhoneTouchPointsSerializer(phone_touchpoint_data, many=True)
                            count_call=0
                            map_calls={}
                            count_completed_call=0
                            connected=0
                            removed=0
                            meetingsSetup_calls=0
                            

                            for touchpoint in serializer.data:
                                if touchpoint.get('contact_id') not in map_calls:
                                    if touchpoint.get('pstatus')=="Completed":    
                                        map_calls[touchpoint.get('contact_id')]="Completed"
                                    else:
                                        map_calls[touchpoint.get('contact_id')]="Not Completed"
                                elif touchpoint.get('pstatus')=="Completed":
                                    map_calls[touchpoint.get('contact_id')]="Completed"

                                if touchpoint.get('pstatus')=="CONNECTED":
                                    connected+=1
                                if touchpoint.get('pstatus')=="REMOVED":
                                    removed+=1   
                                if touchpoint.get('pstatus')=="MEETING SCHEDULED":
                                    meetingsSetup_calls+=1
                                

                            for (key,value) in map_calls.items():
                                if value=="Completed":
                                    count_completed_call+=1
                                count_call+=1 

                                    
                            
                            json={
                                "salesperson_id":salesperson['salesperson_id'],
                                "salesperson_name":salesperson['salesperson_name'],
                                "campaignId":campaign["campaign_id"],
                                "campaignStatus":campaign["campaign_status"],
                                "campaignName":campaign["campaign_name"],
                                "createdDate":campaign["created_ts"],
                                "leads":campaign["no_of_leads"],
                                "campaignStartedLinkedIn":round((float(count_linkedinmessages)/float(campaign["no_of_leads"]))*100,2),
                                "campaignStartedCalls":round((float(meetingsSetup_calls)/float(campaign["no_of_leads"]))*100,2),
                                "campaignStartedEmail":round((float(count_emails)/float(campaign["no_of_leads"]))*100,2),
                                "campaignActive":campaign["campaign_status"]=='In Progress',
                                "linkedIn":{
                                    "campaignStarted":count_linkedinmessages,
                                    "campaignCompleted":count_completed_linkedin,
                                    "acceptedConnectionRequest":connection_request,
                                    "respondedToInMail":inmail_responded,
                                    "meetingsSetup":meetingsSetup_linkedin,
                                },
                                "calls":{
                                    "campaignStarted":count_call,
                                    "campaignCompleted":count_completed_call,
                                    "connected":connected,
                                    "removedFromList":removed,
                                    "meetingsSetup":meetingsSetup_calls,
                                },
                                "emails":{
                                    "campaignStarted":count_emails,
                                    "campaignCompleted":count_completed_email,
                                    "delivered":delivered,
                                    "unsubscribe":unsubscribe,
                                    "responded":responded,
                                    "meetingsSetup":meetingsSetup,
                                }
                            }

                            # final_arr.append(json)
                            final_sales_data.append(json)

                # print(final_arr)
                return Response({"status":"Success","json":final_sales_data}, status=status.HTTP_200_OK)
            else:
                return Response("Bad Request.Invalid User type", status=status.HTTP_200_OK)
                    

        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#for user and admin
class ActiveCampaignList(APIView):
    serializer = PhoneTouchPointsSerializer(PhoneTouchPointsSerializer, many=True)
    serializer_linkedin = LinkedInTouchPointsSerializer(LinkedInTouchPointsSerializer, many=True)
    serializer_email = EmailTouchPointsSerializer(EmailTouchPointsSerializer, many=True)
    def get(self, request):
        try:
            user_type=request.headers['Scope']
            if user_type=="User":
                final_arr=[]
                userId = request.headers['Userid']
                print(userId)
                # Get all campaigns
                campaigns = CampaignSalesPersonMappingInfo.objects.filter(salesperson_id=userId).values('campaign_id')
                for campaign in campaigns:
                    campaigns_list = list(CampaignInfo.objects.filter(campaign_id=campaign['campaign_id'],campaign_status='In Progress').values())

                    
                    for campaign in campaigns_list:
                        
                        #emails touchpoints
                        email_touchpoint_data = EmailTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_email=EmailTouchPointsSerializer(email_touchpoint_data, many=True)
                        count_emails=0
                        # print(serializer_email.data)
                        map={}
                        count_completed_email=0
                        delivered=0
                        unsubscribe=0
                        responded=0
                        meetingsSetup=0

                        for touchpoint in serializer_email.data:
                            if touchpoint.get('contact_id') not in map:
                                if touchpoint.get('estatus')=="Completed":    
                                    map[touchpoint.get('contact_id')]="Completed"
                                else:
                                    map[touchpoint.get('contact_id')]="Not Completed"
                            elif touchpoint.get('estatus')=="Completed":
                                map[touchpoint.get('contact_id')]="Completed"

                            if touchpoint.get('etype')=="DELIVERED":
                                delivered+=1
                            if touchpoint.get('etype')=="UNSUBSCRIBED":
                                unsubscribe+=1   
                            if touchpoint.get('etype')=="RESPONDED":
                                responded+=1
                            if touchpoint.get('etype')=="MEETINGS":
                                meetingsSetup+=1 

                        for (key,value) in map.items():
                            if value=="Completed":
                                count_completed_email+=1
                            count_emails+=1          
                        
                        #linkedIn touchpoints
                        linkedin_touchpoint_data = LinkedInTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_linkedin=LinkedInTouchPointsSerializer(linkedin_touchpoint_data, many=True)
                        count_linkedinmessages=0
                        map_linkedin={}
                        count_completed_linkedin=0
                        connection_request=0
                        inmail_responded=0
                        meetingsSetup_linkedin=0
                        

                        for touchpoint in serializer_linkedin.data:
                            if touchpoint.get('contact_id') not in map:
                                if touchpoint.get('lstatus')=="Completed":    
                                    map_linkedin[touchpoint.get('contact_id')]="Completed"
                                else:
                                    map_linkedin[touchpoint.get('contact_id')]="Not Completed"
                            elif touchpoint.get('lstatus')=="Completed":
                                map_linkedin[touchpoint.get('contact_id')]="Completed"

                            if touchpoint.get('tp_type')=="CONNECTION REQUEST SENT":
                                connection_request+=1
                            if touchpoint.get('tp_type')=="INMAIL SENT":
                                inmail_responded+=1   
                            if touchpoint.get('tp_type')=="MEETING SCHEDULED":
                                meetingsSetup_linkedin+=1
                            

                        for (key,value) in map_linkedin.items():
                            if value=="Completed":
                                count_completed_linkedin+=1
                            count_linkedinmessages+=1  
                        
                        #calls touchpoints
                        phone_touchpoint_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer=PhoneTouchPointsSerializer(phone_touchpoint_data, many=True)
                        count_call=0
                        map_calls={}
                        count_completed_call=0
                        connected=0
                        removed=0
                        meetingsSetup_calls=0
                        

                        for touchpoint in serializer.data:
                            if touchpoint.get('contact_id') not in map_calls:
                                if touchpoint.get('pstatus')=="Completed":    
                                    map_calls[touchpoint.get('contact_id')]="Completed"
                                else:
                                    map_calls[touchpoint.get('contact_id')]="Not Completed"
                            elif touchpoint.get('pstatus')=="Completed":
                                map_calls[touchpoint.get('contact_id')]="Completed"

                            if touchpoint.get('pstatus')=="CONNECTED":
                                connected+=1
                            if touchpoint.get('pstatus')=="REMOVED":
                                removed+=1   
                            if touchpoint.get('pstatus')=="MEETING SCHEDULED":
                                meetingsSetup_calls+=1
                            

                        for (key,value) in map_calls.items():
                            if value=="Completed":
                                count_completed_call+=1
                            count_call+=1 

                                
                        
                        json={
                            "campaignId":campaign["campaign_id"],
                            "campaignStatus":campaign["campaign_status"],
                            "campaignName":campaign["campaign_name"],
                            "createdDate":campaign["created_ts"],
                            "leads":campaign["no_of_leads"],
                            "campaignStartedLinkedIn":round((float(count_linkedinmessages)/float(campaign["no_of_leads"]))*100,2),
                            "campaignStartedCalls":round((float(meetingsSetup_calls)/float(campaign["no_of_leads"]))*100,2),
                            "campaignStartedEmail":round((float(count_emails)/float(campaign["no_of_leads"]))*100,2),
                            "campaignActive":campaign["campaign_status"]=='In Progress',
                            "linkedIn":{
                                "campaignStarted":count_linkedinmessages,
                                "campaignCompleted":count_completed_linkedin,
                                "acceptedConnectionRequest":connection_request,
                                "respondedToInMail":inmail_responded,
                                "meetingsSetup":meetingsSetup_linkedin,
                            },
                            "calls":{
                                "campaignStarted":count_call,
                                "campaignCompleted":count_completed_call,
                                "connected":connected,
                                "removedFromList":removed,
                                "meetingsSetup":meetingsSetup_calls,
                            },
                            "emails":{
                                "campaignStarted":count_emails,
                                "campaignCompleted":count_completed_email,
                                "delivered":delivered,
                                "unsubscribe":unsubscribe,
                                "responded":responded,
                                "meetingsSetup":meetingsSetup,
                            }
                        }

                        final_arr.append(json)


                # print(final_arr)
                return Response({"status":"Success","json":final_arr}, status=status.HTTP_200_OK)
            elif user_type=="Admin":
                salespersons=SalesPersonInfo.objects.all().values('salesperson_id','salesperson_name')
                # final_arr=[]
                final_sales_data=[]
                for salesperson in salespersons:
                    userId=salesperson['salesperson_id']
                    final_arr=[]
                    campaigns = CampaignSalesPersonMappingInfo.objects.filter(salesperson_id=userId).values('campaign_id')
                    for campaign in campaigns:
                        campaigns_list = list(CampaignInfo.objects.filter(campaign_id=campaign['campaign_id'],campaign_status='In Progress').values())

                        
                        for campaign in campaigns_list:
                            
                            #emails touchpoints
                            email_touchpoint_data = EmailTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                            serializer_email=EmailTouchPointsSerializer(email_touchpoint_data, many=True)
                            count_emails=0
                            # print(serializer_email.data)
                            map={}
                            count_completed_email=0
                            delivered=0
                            unsubscribe=0
                            responded=0
                            meetingsSetup=0

                            for touchpoint in serializer_email.data:
                                if touchpoint.get('contact_id') not in map:
                                    if touchpoint.get('estatus')=="Completed":    
                                        map[touchpoint.get('contact_id')]="Completed"
                                    else:
                                        map[touchpoint.get('contact_id')]="Not Completed"
                                elif touchpoint.get('estatus')=="Completed":
                                    map[touchpoint.get('contact_id')]="Completed"

                                if touchpoint.get('etype')=="DELIVERED":
                                    delivered+=1
                                if touchpoint.get('etype')=="UNSUBSCRIBED":
                                    unsubscribe+=1   
                                if touchpoint.get('etype')=="RESPONDED":
                                    responded+=1
                                if touchpoint.get('etype')=="MEETINGS":
                                    meetingsSetup+=1 

                            for (key,value) in map.items():
                                if value=="Completed":
                                    count_completed_email+=1
                                count_emails+=1          
                            
                            #linkedIn touchpoints
                            linkedin_touchpoint_data = LinkedInTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                            serializer_linkedin=LinkedInTouchPointsSerializer(linkedin_touchpoint_data, many=True)
                            count_linkedinmessages=0
                            map_linkedin={}
                            count_completed_linkedin=0
                            connection_request=0
                            inmail_responded=0
                            meetingsSetup_linkedin=0
                            

                            for touchpoint in serializer_linkedin.data:
                                if touchpoint.get('contact_id') not in map:
                                    if touchpoint.get('lstatus')=="Completed":    
                                        map_linkedin[touchpoint.get('contact_id')]="Completed"
                                    else:
                                        map_linkedin[touchpoint.get('contact_id')]="Not Completed"
                                elif touchpoint.get('lstatus')=="Completed":
                                    map_linkedin[touchpoint.get('contact_id')]="Completed"

                                if touchpoint.get('tp_type')=="CONNECTION REQUEST SENT":
                                    connection_request+=1
                                if touchpoint.get('tp_type')=="INMAIL SENT":
                                    inmail_responded+=1   
                                if touchpoint.get('tp_type')=="MEETING SCHEDULED":
                                    meetingsSetup_linkedin+=1
                                

                            for (key,value) in map_linkedin.items():
                                if value=="Completed":
                                    count_completed_linkedin+=1
                                count_linkedinmessages+=1  
                            
                            #calls touchpoints
                            phone_touchpoint_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                            serializer=PhoneTouchPointsSerializer(phone_touchpoint_data, many=True)
                            count_call=0
                            map_calls={}
                            count_completed_call=0
                            connected=0
                            removed=0
                            meetingsSetup_calls=0
                            

                            for touchpoint in serializer.data:
                                if touchpoint.get('contact_id') not in map_calls:
                                    if touchpoint.get('pstatus')=="Completed":    
                                        map_calls[touchpoint.get('contact_id')]="Completed"
                                    else:
                                        map_calls[touchpoint.get('contact_id')]="Not Completed"
                                elif touchpoint.get('pstatus')=="Completed":
                                    map_calls[touchpoint.get('contact_id')]="Completed"

                                if touchpoint.get('pstatus')=="CONNECTED":
                                    connected+=1
                                if touchpoint.get('pstatus')=="REMOVED":
                                    removed+=1   
                                if touchpoint.get('pstatus')=="MEETING SCHEDULED":
                                    meetingsSetup_calls+=1
                                

                            for (key,value) in map_calls.items():
                                if value=="Completed":
                                    count_completed_call+=1
                                count_call+=1 

                                    
                            
                            json={
                                "salesperson_id":salesperson['salesperson_id'],
                                "salesperson_name":salesperson['salesperson_name'],
                                "campaignId":campaign["campaign_id"],
                                "campaignStatus":campaign["campaign_status"],
                                "campaignName":campaign["campaign_name"],
                                "createdDate":campaign["created_ts"],
                                "leads":campaign["no_of_leads"],
                                "campaignStartedLinkedIn":round((float(count_linkedinmessages)/float(campaign["no_of_leads"]))*100,2),
                                "campaignStartedCalls":round((float(meetingsSetup_calls)/float(campaign["no_of_leads"]))*100,2),
                                "campaignStartedEmail":round((float(count_emails)/float(campaign["no_of_leads"]))*100,2),
                                "campaignActive":campaign["campaign_status"]=='In Progress',
                                "linkedIn":{
                                    "campaignStarted":count_linkedinmessages,
                                    "campaignCompleted":count_completed_linkedin,
                                    "acceptedConnectionRequest":connection_request,
                                    "respondedToInMail":inmail_responded,
                                    "meetingsSetup":meetingsSetup_linkedin,
                                },
                                "calls":{
                                    "campaignStarted":count_call,
                                    "campaignCompleted":count_completed_call,
                                    "connected":connected,
                                    "removedFromList":removed,
                                    "meetingsSetup":meetingsSetup_calls,
                                },
                                "emails":{
                                    "campaignStarted":count_emails,
                                    "campaignCompleted":count_completed_email,
                                    "delivered":delivered,
                                    "unsubscribe":unsubscribe,
                                    "responded":responded,
                                    "meetingsSetup":meetingsSetup,
                                }
                            }

                            # final_arr.append(json)
                            final_sales_data.append(json)

                # print(final_arr)
                return Response({"status":"Success","json":final_sales_data}, status=status.HTTP_200_OK)
            else:
                return Response("Bad Request.Invalid User type", status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChangeCampaignStatus(APIView):
    def post(self,request):
        try:
            payload = json.loads(request.body.decode('utf-8'))
            status=payload['campaign_status']
            id=payload['campaign_id']
            print(payload)
            if status:
                CampaignInfo.objects.filter(campaign_id=id).update(campaign_status='In Progress')
            else:
                CampaignInfo.objects.filter(campaign_id=id).update(campaign_status='Completed')

            return Response(data={'status':'Success', 'message':"campaign status Updated successfully"}, status=200)
            
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DripifyDetails(APIView):
    pass

#correct
class Apolloapitest(APIView):
    def post(self, request):
        try:
            payload = json.loads(request.body.decode('utf-8'))
            email = payload['apolloInfoConfig']['username']
            password=payload['apolloInfoConfig']['password']
            # print(email,password)

            
            options = Options()
            options.add_argument("--headless")
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
            driver.find_element(By.NAME, 'email').send_keys(email)
            time.sleep(1)
            driver.find_element(By.NAME, "password").is_displayed()
            driver.find_element(By.NAME, "password").send_keys(password)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))
            time.sleep(2)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            driver.implicitly_wait(10)
            if driver.find_element(By.ID, "side-nav-search").is_displayed():
                return Response(data={'status':'success','message':"Test Passed. Credentials are correct."}, status=status.HTTP_200_OK)
            else:
                return Response(data={'status':'Failed', 'message':"Test Failed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Test Failed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class Dripifyapitest(APIView):
    def post(self, request):
        try:
            payload = json.loads(request.body.decode('utf-8'))
            username = payload['dripifyConfig']['username']
            password=payload['dripifyConfig']['password']
            print(email,password)

            options = Options()
            options.add_argument("--headless")
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
            driver.find_element(By.ID, "email").send_keys(username)
            time.sleep(1)
            driver.find_element(By.ID, "password").send_keys(password)
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[@type='submit']").is_enabled()
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            driver.implicitly_wait(10)
            time.sleep(2)
            if driver.find_element(By.XPATH, "//h2[text()='Statistics']").is_displayed():
                return Response(data={'status':'success','message':"Test Passed. Credentials are correct."}, status=status.HTTP_200_OK)
            else:
                return Response(data={'status':'Failed', 'message':"Test Failed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Test Failed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#correct
class ZoomInfoapitest(APIView):
    def login_to_gmail(self,username,password):
        
        # username='lila.davis@vassardigital.ai'
        # password = 'xcdg ymlx wgyi edgv'

        print("Login to Gmail")
        gmail_host_data = 'imap.gmail.com'
        gmail_port_data = 993
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



    def fetch_first_two_emails(self, mail):
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




    def retrieve_otp_from_email(self,gmail_username,gmail_password):
        # gmail_username='lila.davis@vassardigital.ai'
        # gmail_password = 'xcdg ymlx wgyi edgv'
        
        mail=self.login_to_gmail(gmail_username,gmail_password)
        fetched_data=self.fetch_first_two_emails(mail)
        # print(fetched_data)

        # print(len(fetched_data))
        for i in range(len(fetched_data)):
            body_email=fetched_data[i]['email_body']

            
            otp = re.findall(r'\b\d{6}\b', body_email)
            if otp:
                return otp[0]
        return "No OTP found"
    

    def post(self, request):
        try:
            payload = json.loads(request.body.decode('utf-8'))
            username = payload['zoomInfoConfig']['username']
            password=payload['zoomInfoConfig']['password']
            gmail_address=payload['zoomInfoConfig']['email']
            gmail_password=payload['zoomInfoConfig']['emailPassword']
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            options.add_argument('window-size=1200x600')
            driver = webdriver.Chrome(options=options)
            driver.maximize_window()
            driver.get("https://login.zoominfo.com/")
            time.sleep(2)
            print("opened zoom info")

            driver.find_element(By.ID, 'okta-signin-username').is_displayed()
            driver.find_element(By.ID, 'okta-signin-username').send_keys(username)
            driver.find_element(By.ID, "okta-signin-password").send_keys(password)
            time.sleep(2)
            driver.find_element(By.XPATH, "//input[@id='okta-signin-submit']").is_enabled()
            driver.find_element(By.XPATH, "//input[@id='okta-signin-submit']").click()
            time.sleep(10)
            
            code= self.retrieve_otp_from_email(gmail_address,gmail_password)
            time.sleep(10)

            driver.find_element(By.XPATH, "//input[@id='verify-code-input']").send_keys(code)
            print("code entered")
            time.sleep(2)
            driver.find_element(By.XPATH, "//button[text()='Verify']").click()
            driver.implicitly_wait(120)
            driver.find_element(By.XPATH,
                                "//button[contains(text(),'Advanced Search')]//parent::div//parent::div//input").is_displayed()
            print("inside zoominfo")
            if driver.find_element(By.XPATH,"//button[contains(text(),'Advanced Search')]//parent::div//parent::div//input").is_displayed():
                return Response(data={'status':'success','message':"Test Passed. Credentials are correct."}, status=status.HTTP_200_OK)
            else:
                return Response(data={'status':'Failed', 'message':"Test Failed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Test Failed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#correct
class AdminSaveConfig(APIView):
    def post(self, request):
        try:
            payload = json.loads(request.body.decode('utf-8'))
            # payload={'adminConfigForm': {'zoomInfoFormArray': [{'username': 'lila.davis@vassardigital.ai', 'password': 'Future@Labs2024', 'email': 'lila.davis@vassardigital.ai', 'emailPassword': 'xcdg ymlx wgyi edgv'}], 'apolloConfig': {'username': 'amit@vassarlabs.com', 'password': 'Future@Labs2023'}, 'zeroBounceApiKey': 'dsfsdss', 'sendGridConfig': {'apiKey': 'asdasaa', 'noOfEmailPerDay': 'adsa', 'noOfCampaigns': 'asda', 'day': [False, False, False, False, True, False, False], 'fromTime': '11:34', 'toTime': '11:34', 'timeZone': 'Eastern Time Zone (EST)', 'emailTimeInterval': 'asd'}, 'verifyGmailConfig': {'username': 'lila.davis@vassardigital.ai', 'password': 'xcdg ymlx wgyi edgv'}}}
            
            print(payload)

            zoomInfo=payload["adminConfigForm"]['zoomInfoFormArray']
            apollo=payload["adminConfigForm"]['apolloConfig']
            zeroBounce=payload["adminConfigForm"]['zeroBounceApiKey']
            sendGrid=payload["adminConfigForm"]['sendGridConfig']
            gmailDripify=payload["adminConfigForm"]["verifyGmailConfig"]

            # print(gmailDripify)


            # zoominfo
            for zoominfo in zoomInfo:
                SalesPersonDetails.objects.create(
                    username=zoominfo.get("username"),
                    password=zoominfo.get("password"),
                    user_level="Admin",
                    service="ZoomInfo",
                    created_ts=round(time.time()*1000),
                    updated_ts=round(time.time()*1000)
                )

                SalesPersonDetails.objects.create(
                    username=zoominfo.get("email"),
                    password=zoominfo.get("emailPassword"),
                    user_level="Admin",
                    service="ZoomInfo Gmail",
                    created_ts=round(time.time()*1000),
                    updated_ts=round(time.time()*1000)
                )


            #apollo
            SalesPersonDetails.objects.create(
                username=sendGrid.get("username"),
                password=apollo.get("password"),
                user_level="Admin",
                service="Apollo",
                created_ts=round(time.time()*1000),
                updated_ts=round(time.time()*1000)
            )

            #zero bounce
            SalesPersonDetails.objects.create(
                api_key=zeroBounce,
                user_level="Admin",
                service="ZeroBounce",
                created_ts=round(time.time()*1000),
                updated_ts=round(time.time()*1000)
            )

            #sendgrid
            SalesPersonDetails.objects.create(
                api_key=sendGrid.get("apiKey"),
                user_level="Admin",
                service="SendGrid",
                created_ts=round(time.time()*1000),
                updated_ts=round(time.time()*1000)
            )


            #gmail dripify
            SalesPersonDetails.objects.create(
                username=gmailDripify.get("username"),
                password=gmailDripify.get("password"),
                user_level="Admin",
                service="Dripify Gmail",
                created_ts=round(time.time()*1000),
                updated_ts=round(time.time()*1000)
            )

            return Response(data={'status':'success','message':"Admin Configuration Saved successfully"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Admin Configuration is not saved"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 

class UserSaveConfig(APIView):
    def post(self, request):
        try:
            payload = json.loads(request.body.decode('utf-8'))
            # payload={
            #         "userConfigForm": {
            #             "dripifyConfig": {
            #                 "username": "",
            #                 "password": ""
            #             },
            #             "addEmailforCampaignArray": [
            #                 "hk@gmail.com","himanshuhk@gmail.com"
            #             ],
            #             "googleVoiceConfig": {
            #                 "username": "",
            #                 "password": ""
            #             }
            #         }
            #     }
            
            dripify=payload['userConfigForm']['dripifyConfig']
            emails=payload['userConfigForm']['addEmailforCampaignArray']
            googleVoice=payload['userConfigForm']['verifyGmailConfig']

            
            #dripify
            SalesPersonDetails.objects.create(
                username=dripify.get("username"),
                password=dripify.get("password"),
                user_level="User",
                service="Dripify",
                created_ts=round(time.time()*1000),
                updated_ts=round(time.time()*1000)
            )

            #emails
            for email in emails:
                SalesPersonDetails.objects.create(
                    username=email,
                    user_level="User",
                    service="Campaign",
                    created_ts=round(time.time()*1000),
                    updated_ts=round(time.time()*1000)
                )

            
            #google voice
            SalesPersonDetails.objects.create(
                username=googleVoice.get("username"),
                password=googleVoice.get("password"),
                user_level="User",
                service="Google Voice",
                created_ts=round(time.time()*1000),
                updated_ts=round(time.time()*1000)
            )

            # return Response("success", status=status.HTTP_200_OK)
            return Response(data={'status':'success','message':"Admin Configuration Saved successfully"}, status=status.HTTP_200_OK)
            

        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Admin Configuration is not saved"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#correct 
class VerifyEmailPassword(APIView):
    def post(self, request):
        try:
            payload = json.loads(request.body.decode('utf-8'))
            print(payload)
            username = payload['verifyGmailConfig']['username']
            password=payload['verifyGmailConfig']['password']
            gmail_host_data = 'imap.gmail.com'
            gmail_port_data = 993
            gmail_host = gmail_host_data
            gmail_port = gmail_port_data
            mail = imaplib.IMAP4_SSL(gmail_host, gmail_port)
            mail.login(username, password)
            return Response(data={'status':'success','message':"Test Passed. Credentials are correct."}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Test failed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#for user and admin
class DashBoardMain(APIView):
    def get(self, request):
        try:
            user_type=request.headers['Scope']
            if user_type=="User":
                userId = request.headers['Userid']
                print(userId)
                # Get all campaigns
                campaigns = CampaignSalesPersonMappingInfo.objects.filter(salesperson_id=userId).values('campaign_id')
                total_calls_total = 0
                unique_callers_count_total = 0
                distribution_by_time_slot_total={'8am_12_am': 0, '12pm_3_pm': 0, '3pm_6_pm': 0}
                distribution_by_call_duration_total={'less_than_5_seconds': 0, '5_to_10_seconds': 0, '10_to_30_seconds': 0, 'more_than_30_seconds': 0}
                
                connection_request_sent_total = 0
                connection_request_accepted_total = 0
                messages_sent_total = 0
                messages_received_total = 0
                inmail_sent_total = 0
                inmail_received_total = 0


                delivered_mail_total = 0
                opened_mail_total=0
                spam_mail_total=0
                bounced_mail_total=0
                unsubscribed_mail_total=0
                clicked_mail_total=0
                responded_mail_total=0

                for campaign in campaigns:
                    # Total number of calls
                    phone_touchpoints_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])

                    # Initialize counters for statistics
                    total_calls = 0
                    unique_callers = set()
                    distribution_by_time_slot = {'8am_12_am': 0, '12pm_3_pm': 0, '3pm_6_pm': 0}
                    distribution_by_call_duration = {'less_than_5_seconds': 0, '5_to_10_seconds': 0, '10_to_30_seconds': 0, 'more_than_30_seconds': 0}

                    # Iterate through each phone touchpoint data
                    for touchpoint in phone_touchpoints_data:
                        # Increment total calls
                        total_calls += 1
                        print(touchpoint.start_time,touchpoint.end_time)
                        # Add caller to unique_callers set
                        unique_callers.add(touchpoint.contact_id)
                        start_time = datetime.strptime(touchpoint.start_time, '%H:%M:%S')
                        end_time = datetime.strptime(touchpoint.end_time, '%H:%M:%S')
                        
                        # Calculate distribution by time slot
                        start_hour = start_time.hour
                        print(start_hour)
                        print(start_hour>=8 and start_hour<=12)
                        if start_hour>=8 and start_hour <= 12:
                            print("here")
                            distribution_by_time_slot['8am_12_am'] += 1
                        elif 12 < start_hour < 15:
                            distribution_by_time_slot['12pm_3_pm'] += 1
                        elif 15 <= start_hour < 18:  
                            distribution_by_time_slot['3pm_6_pm'] += 1


                        print(distribution_by_time_slot)
                        # Calculate distribution by call duration
                        duration = end_time - start_time
                        if duration.total_seconds() < 5:
                            distribution_by_call_duration['less_than_5_seconds'] += 1
                        elif 5 <= duration.total_seconds() < 10:
                            distribution_by_call_duration['5_to_10_seconds'] += 1
                        elif 10 <= duration.total_seconds() < 30:
                            distribution_by_call_duration['10_to_30_seconds'] += 1
                        else:
                            distribution_by_call_duration['more_than_30_seconds'] += 1

                    #distribution by time slot
                    distribution_by_time_slot_total['8am_12_am']+=distribution_by_time_slot['8am_12_am']
                    distribution_by_time_slot_total['12pm_3_pm']+=distribution_by_time_slot['12pm_3_pm']
                    distribution_by_time_slot_total['3pm_6_pm']+=distribution_by_time_slot['3pm_6_pm']

                    #distribution by call duration
                    distribution_by_call_duration_total['less_than_5_seconds']+=distribution_by_call_duration['less_than_5_seconds']
                    distribution_by_call_duration_total['5_to_10_seconds']+=distribution_by_call_duration['5_to_10_seconds']
                    distribution_by_call_duration_total['10_to_30_seconds']+=distribution_by_call_duration['10_to_30_seconds']
                    distribution_by_call_duration_total['more_than_30_seconds']+=distribution_by_call_duration['more_than_30_seconds']
                    
                    
                    total_calls_total = total_calls_total+ total_calls

                    # Convert unique_callers set to count
                    unique_callers_count_total = unique_callers_count_total+ len(unique_callers)
                    connection_request_sent_total =connection_request_sent_total+ LinkedInTouchPoints.objects.filter(tp_type='CONNECTION REQUEST SENT',campaign_id=campaign['campaign_id']).count()
                    connection_request_accepted_total =connection_request_accepted_total+ LinkedInTouchPoints.objects.filter(tp_type='CONNECTION ACCEPTED',campaign_id=campaign['campaign_id']).count()
                    messages_sent_total =messages_sent_total+ LinkedInTouchPoints.objects.filter(tp_type='MESSAGE SENT',campaign_id=campaign['campaign_id']).count()
                    messages_received_total =messages_received_total+ LinkedInTouchPoints.objects.filter(tp_type='MESSAGE RECIEVED',campaign_id=campaign['campaign_id']).count()
                    inmail_sent_total =inmail_sent_total+ LinkedInTouchPoints.objects.filter(tp_type='INMAIL SENT',campaign_id=campaign['campaign_id']).count()
                    inmail_received_total =inmail_received_total+ LinkedInTouchPoints.objects.filter(tp_type='INMAIL RECEIVED',campaign_id=campaign['campaign_id']).count()


                    delivered_mail_total= delivered_mail_total+EmailTouchPoints.objects.filter(etype='DELIVERED',campaign_id=campaign['campaign_id']).count()
                    opened_mail_total=opened_mail_total+EmailTouchPoints.objects.filter(etype='OPENED',campaign_id=campaign['campaign_id']).count()
                    spam_mail_total=spam_mail_total+EmailTouchPoints.objects.filter(etype='SPAM',campaign_id=campaign['campaign_id']).count()
                    bounced_mail_total=bounced_mail_total+EmailTouchPoints.objects.filter(etype='BOUNCED',campaign_id=campaign['campaign_id']).count()
                    unsubscribed_mail_total=unsubscribed_mail_total+EmailTouchPoints.objects.filter(etype='UNSUBSCRIBED',campaign_id=campaign['campaign_id']).count()
                    clicked_mail_total=clicked_mail_total+EmailTouchPoints.objects.filter(etype='CLICKED',campaign_id=campaign['campaign_id']).count()
                    responded_mail_total=responded_mail_total+EmailTouchPoints.objects.filter(etype='RESPONDED',campaign_id=campaign['campaign_id']).count()

                    
                response_data={
                            "calls": {
                                "total": total_calls_total,
                                "uniqueCallers": unique_callers_count_total,
                                "distribution_by_time_slot": distribution_by_time_slot_total,
                                "distribution_by_call_duration": distribution_by_call_duration_total,
                            },
                            "linkedin": {
                                "connection_requests": {
                                    "sent": connection_request_sent_total,
                                    "accepted": connection_request_accepted_total
                                },
                                "messages": {
                                    "sent": messages_sent_total,
                                    "received": messages_received_total
                                },
                                "inmail": {
                                    "sent": inmail_sent_total,
                                    "received": inmail_received_total
                                }
                            },
                            "emails": {
                                "delivered": delivered_mail_total,
                                "opened": opened_mail_total,
                                "spam": spam_mail_total,
                                "bounced": bounced_mail_total,
                                "unsubscribed": unsubscribed_mail_total,
                                "clicked": clicked_mail_total,
                                "responded": responded_mail_total
                            }
                        }
                

                return Response(data={'status':'Success', 'json':response_data}, status=status.HTTP_200_OK)
            elif user_type=="Admin":
                salespersons=SalesPersonInfo.objects.all().values('salesperson_id','salesperson_name')
                final_arr=[]
                for salesperson in salespersons:
                    # Get all campaigns
                    userId=salesperson['salesperson_id']
                    campaigns = CampaignSalesPersonMappingInfo.objects.filter(salesperson_id=userId).values('campaign_id')
                    total_calls_total = 0
                    unique_callers_count_total = 0
                    distribution_by_time_slot_total={'8am_12_am': 0, '12pm_3_pm': 0, '3pm_6_pm': 0}
                    distribution_by_call_duration_total={'less_than_5_seconds': 0, '5_to_10_seconds': 0, '10_to_30_seconds': 0, 'more_than_30_seconds': 0}
                    
                    connection_request_sent_total = 0
                    connection_request_accepted_total = 0
                    messages_sent_total = 0
                    messages_received_total = 0
                    inmail_sent_total = 0
                    inmail_received_total = 0


                    delivered_mail_total = 0
                    opened_mail_total=0
                    spam_mail_total=0
                    bounced_mail_total=0
                    unsubscribed_mail_total=0
                    clicked_mail_total=0
                    responded_mail_total=0

                    for campaign in campaigns:
                        # Total number of calls
                        phone_touchpoints_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])

                        # Initialize counters for statistics
                        total_calls = 0
                        unique_callers = set()
                        distribution_by_time_slot = {'8am_12_am': 0, '12pm_3_pm': 0, '3pm_6_pm': 0}
                        distribution_by_call_duration = {'less_than_5_seconds': 0, '5_to_10_seconds': 0, '10_to_30_seconds': 0, 'more_than_30_seconds': 0}

                        # Iterate through each phone touchpoint data
                        for touchpoint in phone_touchpoints_data:
                            # Increment total calls
                            total_calls += 1
                            print(touchpoint.start_time,touchpoint.end_time)
                            # Add caller to unique_callers set
                            unique_callers.add(touchpoint.contact_id)
                            start_time = datetime.strptime(touchpoint.start_time, '%H:%M:%S')
                            end_time = datetime.strptime(touchpoint.end_time, '%H:%M:%S')
                            
                            # Calculate distribution by time slot
                            start_hour = start_time.hour
                            print(start_hour)
                            print(start_hour>=8 and start_hour<=12)
                            if start_hour>=8 and start_hour <= 12:
                                print("here")
                                distribution_by_time_slot['8am_12_am'] += 1
                            elif 12 < start_hour < 15:
                                distribution_by_time_slot['12pm_3_pm'] += 1
                            elif 15 <= start_hour < 18:  
                                distribution_by_time_slot['3pm_6_pm'] += 1


                            print(distribution_by_time_slot)
                            # Calculate distribution by call duration
                            duration = end_time - start_time
                            if duration.total_seconds() < 5:
                                distribution_by_call_duration['less_than_5_seconds'] += 1
                            elif 5 <= duration.total_seconds() < 10:
                                distribution_by_call_duration['5_to_10_seconds'] += 1
                            elif 10 <= duration.total_seconds() < 30:
                                distribution_by_call_duration['10_to_30_seconds'] += 1
                            else:
                                distribution_by_call_duration['more_than_30_seconds'] += 1

                        #distribution by time slot
                        distribution_by_time_slot_total['8am_12_am']+=distribution_by_time_slot['8am_12_am']
                        distribution_by_time_slot_total['12pm_3_pm']+=distribution_by_time_slot['12pm_3_pm']
                        distribution_by_time_slot_total['3pm_6_pm']+=distribution_by_time_slot['3pm_6_pm']

                        #distribution by call duration
                        distribution_by_call_duration_total['less_than_5_seconds']+=distribution_by_call_duration['less_than_5_seconds']
                        distribution_by_call_duration_total['5_to_10_seconds']+=distribution_by_call_duration['5_to_10_seconds']
                        distribution_by_call_duration_total['10_to_30_seconds']+=distribution_by_call_duration['10_to_30_seconds']
                        distribution_by_call_duration_total['more_than_30_seconds']+=distribution_by_call_duration['more_than_30_seconds']
                        
                        
                        total_calls_total = total_calls_total+ total_calls

                        # Convert unique_callers set to count
                        unique_callers_count_total = unique_callers_count_total+ len(unique_callers)
                        connection_request_sent_total =connection_request_sent_total+ LinkedInTouchPoints.objects.filter(tp_type='CONNECTION REQUEST SENT',campaign_id=campaign['campaign_id']).count()
                        connection_request_accepted_total =connection_request_accepted_total+ LinkedInTouchPoints.objects.filter(tp_type='CONNECTION ACCEPTED',campaign_id=campaign['campaign_id']).count()
                        messages_sent_total =messages_sent_total+ LinkedInTouchPoints.objects.filter(tp_type='MESSAGE SENT',campaign_id=campaign['campaign_id']).count()
                        messages_received_total =messages_received_total+ LinkedInTouchPoints.objects.filter(tp_type='MESSAGE RECIEVED',campaign_id=campaign['campaign_id']).count()
                        inmail_sent_total =inmail_sent_total+ LinkedInTouchPoints.objects.filter(tp_type='INMAIL SENT',campaign_id=campaign['campaign_id']).count()
                        inmail_received_total =inmail_received_total+ LinkedInTouchPoints.objects.filter(tp_type='INMAIL RECEIVED',campaign_id=campaign['campaign_id']).count()


                        delivered_mail_total= delivered_mail_total+EmailTouchPoints.objects.filter(etype='DELIVERED',campaign_id=campaign['campaign_id']).count()
                        opened_mail_total=opened_mail_total+EmailTouchPoints.objects.filter(etype='OPENED',campaign_id=campaign['campaign_id']).count()
                        spam_mail_total=spam_mail_total+EmailTouchPoints.objects.filter(etype='SPAM',campaign_id=campaign['campaign_id']).count()
                        bounced_mail_total=bounced_mail_total+EmailTouchPoints.objects.filter(etype='BOUNCED',campaign_id=campaign['campaign_id']).count()
                        unsubscribed_mail_total=unsubscribed_mail_total+EmailTouchPoints.objects.filter(etype='UNSUBSCRIBED',campaign_id=campaign['campaign_id']).count()
                        clicked_mail_total=clicked_mail_total+EmailTouchPoints.objects.filter(etype='CLICKED',campaign_id=campaign['campaign_id']).count()
                        responded_mail_total=responded_mail_total+EmailTouchPoints.objects.filter(etype='RESPONDED',campaign_id=campaign['campaign_id']).count()

                        
                    response_data={
                                "calls": {
                                    "total": total_calls_total,
                                    "uniqueCallers": unique_callers_count_total,
                                    "distribution_by_time_slot": distribution_by_time_slot_total,
                                    "distribution_by_call_duration": distribution_by_call_duration_total,
                                },
                                "linkedin": {
                                    "connection_requests": {
                                        "sent": connection_request_sent_total,
                                        "accepted": connection_request_accepted_total
                                    },
                                    "messages": {
                                        "sent": messages_sent_total,
                                        "received": messages_received_total
                                    },
                                    "inmail": {
                                        "sent": inmail_sent_total,
                                        "received": inmail_received_total
                                    }
                                },
                                "emails": {
                                    "delivered": delivered_mail_total,
                                    "opened": opened_mail_total,
                                    "spam": spam_mail_total,
                                    "bounced": bounced_mail_total,
                                    "unsubscribed": unsubscribed_mail_total,
                                    "clicked": clicked_mail_total,
                                    "responded": responded_mail_total
                                }
                            }
                    
                    final_arr.append({'salesperson_id':salesperson['salesperson_id'],'salesperson_name':salesperson['salesperson_name'],'data':response_data})
                
                return Response(data={'status':'Success', 'json':final_arr}, status=status.HTTP_200_OK)
            else:
                return Response("Bad Request.Invalid User type", status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Test failed.Test Passed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#for user and admin
class DashBoardMainInside(APIView):
    serializer = PhoneTouchPointsSerializer(PhoneTouchPointsSerializer, many=True)
    serializer_linkedin = LinkedInTouchPointsSerializer(LinkedInTouchPointsSerializer, many=True)
    serializer_email = EmailTouchPointsSerializer(EmailTouchPointsSerializer, many=True)
    
    def get_call_data(self, total_calls):
        try:
            pass   
            call_data=[]

            for call in total_calls:
                # contact_instance=PhoneTouchPoints(call)
                print(call["contact_id"])
                contact=ContactInfo.objects.filter(contact_id=call["contact_id"]).values('first_name','last_name','linkedin_id_url','direct_landline','mobile_number','customer_id')
                # print(contact['customer_id'])

                call_data.append({
                    "contactId":call['contact_id'],
                    "campaignId":call['campaign_id'],
                    "customerId":str(contact[0]['customer_id']),
                    "contactName": f"{contact[0]['first_name']} {contact[0]['last_name']}",
                    "companyName": "Tesla",  # Assuming company name is constant here
                    "linkedInId": contact[0]['linkedin_id_url'],
                    "phone": contact[0]['direct_landline'],
                    "email": contact[0]['mobile_number'],
                    "dateTime": str(datetime.fromtimestamp(int(call['date']))),
                    "numSeconds": 30  # Assuming call duration is constant
                })
            
            # print(call_data)
            return call_data

            
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Test failed.Test Passed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_linkedin_data(self,total_messages):
        try:
            pass   
            message_data=[]

            for message in total_messages:
                # contact_instance=PhoneTouchPoints(call)
                print(message["contact_id"])
                contact=ContactInfo.objects.filter(contact_id=message["contact_id"]).values('first_name','last_name','linkedin_id_url','direct_landline','mobile_number','customer_id')
                
                message_data.append({
                    "contactId":message["contact_id"],
                    "campaignId":message['campaign_id'],
                    "customerId":str(contact[0]['customer_id']),
                    "contactName": f"{contact[0]['first_name']} {contact[0]['last_name']}",
                    "companyName": "Tesla",  # Assuming company name is constant here
                    "linkedInId": contact[0]['linkedin_id_url'],
                    "phone": contact[0]['direct_landline'],
                    "email": contact[0]['mobile_number'],
                    "dateTime": str(datetime.fromtimestamp(int(message['date']))),
                    "numSeconds": 30  # Assuming call duration is constant
                })
            
            # print(call_data)
            return message_data

            
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Test failed.Test Passed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_email_data(self,total_emails):
        try:
            pass   
            message_data=[]

            for message in total_emails:
                print(message["contact_id"])
                contact=ContactInfo.objects.filter(contact_id=message["contact_id"]).values('first_name','last_name','linkedin_id_url','direct_landline','mobile_number','customer_id')
                
                message_data.append({
                    "contactId":message["contact_id"],
                    "campaignId":message['campaign_id'],
                    "customerId":str(contact[0]['customer_id']),
                    "contactName": f"{contact[0]['first_name']} {contact[0]['last_name']}",
                    "companyName": "Tesla",  # Assuming company name is constant here
                    "linkedInId": contact[0]['linkedin_id_url'],
                    "phone": contact[0]['direct_landline'],
                    "email": contact[0]['mobile_number'],
                    "dateTime": str(datetime.fromtimestamp(int(message['date']))),
                    "numSeconds": 30  # Assuming call duration is constant
                })
            
            # print(call_data)
            return message_data

            
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Test failed.Test Passed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def post(self, request):
        try:
            pass
            payload = json.loads(request.body.decode('utf-8'))
            # print(payload)
            
            # json_data=[]
            # payload={
            #     'header':'Calls',
            #     'subHeader':'total'
            # }
            userId = request.headers['Userid']
            scope_user=request.headers['Scope']
            if scope_user=="Admin":
                userId = payload['Userid']
            # print(userId)
            # Get all campaigns
            campaigns = CampaignSalesPersonMappingInfo.objects.filter(salesperson_id=userId).values('campaign_id')
            
            
            header=payload['header']
            subHeader=payload['subHeader']

            headers=['Calls','LinkedIn','Emails']
            callsSubheader =[
                'total',
                'uniqueCallers',
                '8am_12_am',
                '12pm_3_pm',
                '3pm_6_pm',
                'less_than_5_seconds',
                '5_to_10_seconds',
                '10_to_30_seconds',
                'more_than_30_seconds'
                ]
            linkedinSubheader=[
                'connection_requests_sent',
                'connection_requests_accepted',
                'messages_sent',
                'messages_received',
                'inmail_sent',
                'inmail_received'
                ]
            emailsSubheader=[
                'delivered',
                'opened',
                'spam',
                'bounced',
                'unsubscribed',
                'clicked',
                'responded'
                ]
            
            if header=='Calls':
                if subHeader=="total":
                    total_calls=[]
                    for campaign in campaigns:
                        phone_touchpoints_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer = PhoneTouchPointsSerializer(phone_touchpoints_data, many=True)
                        # print(serializer.data)
                        
                        for touchpoint in serializer.data:
                            total_calls.append(touchpoint)

                    json_data=self.get_call_data(total_calls)   
                     

                elif subHeader=="uniqueCallers":
                    total_calls = []
                    for campaign in campaigns:
                        unique_callers = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer = PhoneTouchPointsSerializer(unique_callers, many=True)
                    
                        print(serializer.data)
                        id_set = set()

                        for touchpoint in serializer.data:
                            contact_id = touchpoint.get('contact_id')
                            if contact_id not in id_set:
                                total_calls.append(touchpoint)
                                id_set.add(contact_id)

                    json_data=self.get_call_data(total_calls)

                    
                elif subHeader=="8am_12_am":
                    total_calls=[]
                    for campaign in campaigns:
                        phone_touchpoints_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer = PhoneTouchPointsSerializer(phone_touchpoints_data, many=True)
                    
                        for touchpoint in serializer.data:               
                            start_time = datetime.strptime(touchpoint.get('start_time'), '%H:%M:%S')
                            end_time = datetime.strptime(touchpoint.get('end_time'), '%H:%M:%S')
                            
                            # Calculate distribution by time slot
                            start_hour = start_time.hour
                            if 8 <= start_hour < 12:
                                total_calls.append(touchpoint)
                    
                    json_data=self.get_call_data(total_calls) 
                    
                elif subHeader=='12pm_3_pm':
                    total_calls=[]
                    for campaign in campaigns:
                        phone_touchpoints_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer = PhoneTouchPointsSerializer(phone_touchpoints_data, many=True)
                        
                        for touchpoint in serializer.data:               
                            start_time = datetime.strptime(touchpoint.get('start_time'), '%H:%M:%S')
                            end_time = datetime.strptime(touchpoint.get('end_time'), '%H:%M:%S')
                            
                            # Calculate distribution by time slot
                            start_hour = start_time.hour
                            if 12 <= start_hour < 15:
                                total_calls.append(touchpoint)

                    json_data=self.get_call_data(total_calls) 
                elif subHeader=='3pm_6_pm':
                    total_calls=[]
                    for campaign in campaigns:
                        phone_touchpoints_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer = PhoneTouchPointsSerializer(phone_touchpoints_data, many=True)
                        # total_calls=[]
                        for touchpoint in serializer.data:               
                            start_time = datetime.strptime(touchpoint.get('start_time'), '%H:%M:%S')
                            end_time = datetime.strptime(touchpoint.get('end_time'), '%H:%M:%S')
                            
                            # Calculate distribution by time slot
                            start_hour = start_time.hour   
                            # print(start_hour)       
                            if 15 <= start_hour < 18:
                                total_calls.add(touchpoint)
                    
                    # print("I am here")
                    json_data=self.get_call_data(total_calls) 

                elif subHeader=='less_than_5_seconds':
                    total_calls=[]
                    for campaign in campaigns:
                        phone_touchpoints_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer = PhoneTouchPointsSerializer(phone_touchpoints_data, many=True)
                        # total_calls=[]
                        for touchpoint in serializer.data:               
                            start_time = datetime.strptime(touchpoint.get('start_time'), '%H:%M:%S')
                            end_time = datetime.strptime(touchpoint.get('end_time'), '%H:%M:%S')
                            
                            duration = end_time - start_time
                            if duration.total_seconds() < 5:
                                total_calls.append(touchpoint)
                    json_data=self.get_call_data(total_calls) 
                elif subHeader=='5_to_10_seconds':
                    total_calls=[]
                    for campaign in campaigns:
                        phone_touchpoints_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer = PhoneTouchPointsSerializer(phone_touchpoints_data, many=True)
                        # total_calls=[]
                        for touchpoint in serializer.data:               
                            start_time = datetime.strptime(touchpoint.get('start_time'), '%H:%M:%S')
                            end_time = datetime.strptime(touchpoint.get('end_time'), '%H:%M:%S')
                            
                            duration = end_time - start_time
                            if duration.total_seconds() < 10 and duration.total_seconds() >= 5:
                                total_calls.append(touchpoint)
                    json_data=self.get_call_data(total_calls) 
                elif subHeader=='10_to_30_seconds':
                    total_calls=[]
                    for campaign in campaigns:
                        phone_touchpoints_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer = PhoneTouchPointsSerializer(phone_touchpoints_data, many=True)
                        # total_calls=[]
                        for touchpoint in serializer.data:               
                            start_time = datetime.strptime(touchpoint.get('start_time'), '%H:%M:%S')
                            end_time = datetime.strptime(touchpoint.get('end_time'), '%H:%M:%S')
                            
                            duration = end_time - start_time
                            if duration.total_seconds() < 30 and duration.total_seconds() >= 10:
                                total_calls.append(touchpoint)
                    json_data=self.get_call_data(total_calls) 
                elif subHeader=='more_than_30_seconds':
                    total_calls=[]
                    for campaign in campaigns:
                        phone_touchpoints_data = PhoneTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer = PhoneTouchPointsSerializer(phone_touchpoints_data, many=True)
                        # total_calls=[]
                        for touchpoint in serializer.data:               
                            start_time = datetime.strptime(touchpoint.get('start_time'), '%H:%M:%S')
                            end_time = datetime.strptime(touchpoint.get('end_time'), '%H:%M:%S')
                            
                            duration = end_time - start_time
                            if duration.total_seconds() >=30 :
                                total_calls.append(touchpoint)
                    json_data=self.get_call_data(total_calls) 

            elif header=="LinkedIn":
                if subHeader=="connection_requests_sent":
                    total_messages=[]
                    for campaign in campaigns:
                        linkedin_touchpoint_data = LinkedInTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_linkedin=LinkedInTouchPointsSerializer(linkedin_touchpoint_data, many=True)
                        # total_messages=[]
                        for touchpoint in serializer_linkedin.data:
                            if touchpoint.get('tp_type')=='CONNECTION REQUEST SENT':
                                total_messages.append(touchpoint)
                    
                    print(total_messages)
                    json_data=self.get_linkedin_data(total_messages)
                elif subHeader=='connection_requests_accepted':
                    total_messages=[]
                    for campaign in campaigns:
                        linkedin_touchpoint_data = LinkedInTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_linkedin=LinkedInTouchPointsSerializer(linkedin_touchpoint_data, many=True)
                        # total_messages=[]
                        for touchpoint in serializer_linkedin.data:
                            if touchpoint.get('tp_type')=='CONNECTION ACCEPTED':
                                total_messages.append(touchpoint)
                    
                    # print(total_messages)
                    json_data=self.get_linkedin_data(total_messages)
                elif subHeader=='messages_sent':
                    total_messages=[]
                    for campaign in campaigns:
                        linkedin_touchpoint_data = LinkedInTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_linkedin=LinkedInTouchPointsSerializer(linkedin_touchpoint_data, many=True)
                        # total_messages=[]
                        for touchpoint in serializer_linkedin.data:
                            if touchpoint.get('tp_type')=='MESSAGE SENT':
                                total_messages.append(touchpoint)
                    
                    # print(total_messages)
                    json_data=self.get_linkedin_data(total_messages)
                elif subHeader=='messages_received':
                    total_messages=[]
                    for campaign in campaigns:
                        linkedin_touchpoint_data = LinkedInTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        linkedin_touchpoint_data = LinkedInTouchPoints.objects.all()
                        serializer_linkedin=LinkedInTouchPointsSerializer(linkedin_touchpoint_data, many=True)
                        # total_messages=[]
                        for touchpoint in serializer_linkedin.data:
                            if touchpoint.get('tp_type')=='MESSAGE RECIEVED':
                                total_messages.append(touchpoint)
                    
                    # print(total_messages)
                    json_data=self.get_linkedin_data(total_messages)
                elif subHeader=='inmail_sent':
                    total_messages=[]
                    for campaign in campaigns:
                        linkedin_touchpoint_data = LinkedInTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_linkedin=LinkedInTouchPointsSerializer(linkedin_touchpoint_data, many=True)
                        # total_messages=[]
                        for touchpoint in serializer_linkedin.data:
                            if touchpoint.get('tp_type')=='INMAIL SENT':
                                total_messages.append(touchpoint)
                    
                    # print(total_messages)
                    json_data=self.get_linkedin_data(total_messages)
                elif subHeader=='inmail_received':
                    total_messages=[]
                    for campaign in campaigns:
                        linkedin_touchpoint_data = LinkedInTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        # linkedin_touchpoint_data = LinkedInTouchPoints.objects.all()
                        serializer_linkedin=LinkedInTouchPointsSerializer(linkedin_touchpoint_data, many=True)
                        # total_messages=[]
                        for touchpoint in serializer_linkedin.data:
                            if touchpoint.get('tp_type')=='INMAIL RECEIVED':
                                total_messages.append(touchpoint)
                    
                    print(total_messages)
                    json_data=self.get_linkedin_data(total_messages)

            elif header=="Emails":
                if subHeader=="delivered":
                    total_emails=[]
                    for campaign in campaigns:
                        email_touchpoint_data = EmailTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_email=EmailTouchPointsSerializer(email_touchpoint_data, many=True)
                        
                        # print(serializer_email.data)
                        for touchpoint in serializer_email.data:
                            if touchpoint.get('etype')=='DELIVERED':
                                total_emails.append(touchpoint)
                    
                    # print(total_emails)
                    json_data=self.get_email_data(total_emails)
                elif subHeader=="opened":
                    total_emails=[]
                    for campaign in campaigns:
                        email_touchpoint_data = EmailTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_email=EmailTouchPointsSerializer(email_touchpoint_data, many=True)
                        # total_emails=[]
                        # print(serializer_email.data)
                        for touchpoint in serializer_email.data:
                            if touchpoint.get('etype')=='OPENED':
                                total_emails.append(touchpoint)
                    
                    # print(total_emails)
                    json_data=self.get_email_data(total_emails)
                elif subHeader=="spam":

                    total_emails=[]
                    for campaign in campaigns:
                        email_touchpoint_data = EmailTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_email=EmailTouchPointsSerializer(email_touchpoint_data, many=True)
                        # total_emails=[]
                        # print(serializer_email.data)
                        for touchpoint in serializer_email.data:
                            if touchpoint.get('etype')=='SPAM':
                                total_emails.append(touchpoint)
                    
                    # print(total_emails)
                    json_data=self.get_email_data(total_emails)
                elif subHeader=="bounced":
                    total_emails=[]
                    for campaign in campaigns:
                        email_touchpoint_data = EmailTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_email=EmailTouchPointsSerializer(email_touchpoint_data, many=True)
                        # total_emails=[]
                        # print(serializer_email.data)
                        for touchpoint in serializer_email.data:
                            if touchpoint.get('etype')=='BOUNCED':
                                total_emails.append(touchpoint)
                    
                    # print(total_emails)
                    json_data=self.get_email_data(total_emails)
                elif subHeader=="unsubscribed":
                    total_emails=[]
                    for campaign in campaigns:
                        email_touchpoint_data = EmailTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_email=EmailTouchPointsSerializer(email_touchpoint_data, many=True)
                        # total_emails=[]
                        # print(serializer_email.data)
                        for touchpoint in serializer_email.data:
                            if touchpoint.get('etype')=='UNSUBSCRIBED':
                                total_emails.append(touchpoint)
                    
                    # print(total_emails)
                    json_data=self.get_email_data(total_emails)
                elif subHeader=="clicked":
                    total_emails=[]
                    for campaign in campaigns:
                        email_touchpoint_data = EmailTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_email=EmailTouchPointsSerializer(email_touchpoint_data, many=True)
                        # total_emails=[]
                        # print(serializer_email.data)
                        for touchpoint in serializer_email.data:
                            if touchpoint.get('etype')=='CLICKED':
                                total_emails.append(touchpoint)
                    
                    # print(total_emails)
                    json_data=self.get_email_data(total_emails)
                elif subHeader=="responded":
                    total_emails=[]
                    for campaign in campaigns:
                        email_touchpoint_data = EmailTouchPoints.objects.filter(campaign_id=campaign['campaign_id'])
                        serializer_email=EmailTouchPointsSerializer(email_touchpoint_data, many=True)
                        # total_emails=[]
                        # print(serializer_email.data)
                        for touchpoint in serializer_email.data:
                            if touchpoint.get('etype')=='RESPONDED':
                                total_emails.append(touchpoint)
                    
                    # print(total_emails)
                    json_data=self.get_email_data(total_emails)


            # print(json_data)
            # call_data=[
            #     {
            #         "contactName": "Himanshu Kataria",
            #         "companyName": "Tesla",  # Assuming company name is constant here
            #         "linkedInId": "some linked url",
            #         "phone": 9999999945,
            #         "email": "34567882@gmail.com",
            #         "dateTime": "datetime.now().date",
            #         "numSeconds": 30  # Assuming call duration is constant
            #     },
            #     {
            #         "contactName": "Himanshu Kataria",
            #         "companyName": "Tesla",  # Assuming company name is constant here
            #         "linkedInId": "some linked url",
            #         "phone": "9999999945",
            #         "email": "34567882@gmail.com",
            #         "dateTime": "datetime.now().date",
            #         "numSeconds": 30  # Assuming call duration is constant
            #     }
            # ]
            
                

            return Response(data={'status':'Success', 'json':json_data}, status=status.HTTP_200_OK)

            
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Test failed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class DeleteContactsDashboard(APIView):    
    def post(self,request):
        try:
            payload = json.loads(request.body.decode('utf-8'))
            print(payload)
            if payload['type'] == 'Calls':
                contact_to_delete = PhoneTouchPoints.objects.get(ptp_id=payload['contact_id'])
                contact_to_delete.delete()
                print("working")
            elif payload['type']=='linkedIn':
                contact_to_delete = LinkedInTouchPoints.objects.get(ltp_id=payload['contact_id'])
                contact_to_delete.delete()
            else:
                contact_to_delete = EmailTouchPoints.objects.get(etouchpoint_id=payload['contact_id'])
                contact_to_delete.delete()

            return Response(data={'status':'Success', 'message':"Contact deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Test failed.Test Passed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#for user
class NextBestActions(APIView):
    def get(self, request):
        try:
            data_array=[]
            userId = request.headers['Userid']
            print(userId)
            # Get all campaigns
            campaigns = CampaignSalesPersonMappingInfo.objects.filter(salesperson_id=userId).values('campaign_id')
            
            for campaign in campaigns:
                #linkedIn
                message_recieved=LinkedInTouchPoints.objects.filter(tp_type='MESSAGE RECIEVED',campaign_id=campaign['campaign_id']).values('date','contact_id','campaign_id')
                for message in message_recieved:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"linkedIn",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"MESSAGE RECIEVED",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date())
                        }
                    )
                    
                # print(data_array)
                message_sent=LinkedInTouchPoints.objects.filter(tp_type='MESSAGE SENT',campaign_id=campaign['campaign_id']).values('date','contact_id','campaign_id')
                for message in message_sent:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"linkedIn",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"MESSAGE SENT",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date())
                        }
                    )

                connection_accepted=LinkedInTouchPoints.objects.filter(tp_type='CONNECTION ACCEPTED',campaign_id=campaign['campaign_id']).values('date','contact_id','campaign_id')
                # print(connection_accepted)
                for message in message_recieved:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"linkedIn",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"CONNECTION ACCEPTED",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date())
                        }
                    )

                #email
                #delivered
                delivered_mail=EmailTouchPoints.objects.filter(etype='DELIVERED',campaign_id=campaign['campaign_id']).values('date','contact_id','campaign_id')
                # print(delivered_mail, "delivered email")
                for message in delivered_mail:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"email",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"DELIVERED",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date())
                        }
                    )
                    
                
                #responded
                responded_mail=EmailTouchPoints.objects.filter(etype='RESPONDED',campaign_id=campaign['campaign_id']).values('date','contact_id','campaign_id')
                for message in responded_mail:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"email",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"RESPONDED",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date())
                        }
                    )
                    

                
                #calls 
                #responded 
                responded_call=PhoneTouchPoints.objects.filter(pstatus='RESPONDED',campaign_id=campaign['campaign_id']).values('date','contact_id','campaign_id')
                for message in responded_call:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"call",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"RESPONDED",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date())
                        }
                    )

                #not responded
                not_responded_call=PhoneTouchPoints.objects.filter(pstatus='NOT RESPONDED',campaign_id=campaign['campaign_id']).values('date','contact_id','campaign_id')
                for message in not_responded_call:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"call",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"NOT RESPONDED",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date())
                        }
                    )


            map={}
            for data in data_array:
                if data['date'] in map:
                    map[data['date']].append({
                        'type':data['type'],
                        'contactName':data['contactName'],
                        'status':data['status'],
                        'campaign':data['campaign']
                    })
                else:
                    map[data['date']]=[{
                        'type':data['type'],
                        'contactName':data['contactName'],
                        'status':data['status'],
                        'campaign':data['campaign']
                    }]
            arr=[]
            for (key,value) in map.items():
                arr.append({
                    "date":key,
                    "actions":value

                })
                    

            # response_data=[
            #     {
            #         "type":"linkedIn",
            #         "contactName":"Himanshu Kataria",
            #         "status":"MESSAGE SENT/MESSAGE RECIEVED/CONNECTION ACCEPTED",
            #         "campaign":"Deb_Full Flow_MFG_2_GetLeads_500-1000",
            #         "date":str(datetime.now()),
            #     },
            #     {
            #         "type":"linkedIn",
            #         "contactName":"Uday Bhaiya",
            #         "status":"MESSAGE SENT/MESSAGE RECIEVED/CONNECTION ACCEPTED",
            #         "campaign":"Deb_Full Flow_MFG_2_GetLeads_500-1000",
            #         "date":str(datetime.now()),
            #     }
            # ]

            return Response(data={'status':'Passed', 'json':arr}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Test failed.Test Passed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateActivity(APIView):
    def post(self,request):
        try:
            # pass
            payload = json.loads(request.body.decode('utf-8'))
            print(payload)
            
            # payload={
            #     'contact_id':'009bf7aa-c81a-4537-8a85-ede1adb4ae1e',
            #     'campaign_id':'300b8d9b-15c2-45ed-b7e9-fcb03ded7245',
            #     'type':'Phone call/Email/LinkedIn/Meeting Schedule/Notes',
            #     'notes':'some information..',
            #     'date':''
            # }

            contact_id=payload['contact_id']
            campaign_id=payload['campaign_id']
            # activity=payload['activity']
            body_data=payload['notes']
            timestamp = payload['date']
            print(timestamp)

            if payload['type']=='Phone call':
                contact_id_instance = ContactInfo(contact_id=contact_id)
                campaign_id_instance = CampaignInfo(campaign_id=campaign_id)
                # timestamp = datetime.now().timestamp()

                PhoneTouchPoints.objects.create(
                    ptp_id=str(uuid.uuid4()),
                    contact_id=contact_id_instance,
                    campaign_id=campaign_id_instance,
                    date=timestamp,
                    start_time='00:00:00',
                    end_time='00:00:00',
                    # subject=request.data['subject'],
                    pstatus='MANUAL',
                    description=body_data
                    # pstatus=request.data['status'],
                )

            elif payload['type']=='Email':
                # email_template_id = str(uuid.uuid4())
                # EmailTemplate.objects.create(
                #     etemplate_id=email_template_id,
                #     subject=request.data['subject'],
                #     body=request.data['body']
                # )
                contact_id_instance = ContactInfo(contact_id=contact_id)
                campaign_id_instance = CampaignInfo(campaign_id=campaign_id)
                email_template_id_instance = EmailTemplate(etemplate_id='60dc7605-80d0-40b9-90a2-353e0d7662aa')
                # timestamp = datetime.now().strftime('%m-%d-%Y %H:%M:%S')

                EmailTouchPoints.objects.create(
                    etouchpoint_id=str(uuid.uuid4()),
                    contact_id=contact_id_instance,
                    campaign_id=campaign_id_instance,
                    etemplate_id=email_template_id_instance,
                    date=timestamp,
                    # estatus=activity,
                    etype='MANUAL'
                )
            elif payload['type']=='LinkedIn':
                # linkedin_template_id = str(uuid.uuid4())
                # LinkedInTemplate.objects.create(
                #     linkedin_template_id=linkedin_template_id,
                #     template_type=request.data['type'],
                #     body=request.data['body']
                # )
                contact_id_instance = ContactInfo(contact_id=contact_id)
                campaign_id_instance = CampaignInfo(campaign_id=campaign_id)
                # linkedin_template_id_instance = LinkedInTemplate(linkedin_template_id='81607bea-529e-456a-84ef-caea3648b02e')
                # timestamp = datetime.now().strftime('%m-%d-%Y %H:%M:%S')

                LinkedInTouchPoints.objects.create(
                    ltp_id=str(uuid.uuid4()),
                    contact_id=contact_id_instance,
                    campaign_id=campaign_id_instance,
                    linkedin_template_id='81607bea-529e-456a-84ef-caea3648b02e',
                    date=timestamp,
                    tp_type='MANUAL'
                )
            elif payload['type']=='Meeting Schedule':
                contact_id_instance = ContactInfo(contact_id=contact_id)
                campaign_id_instance = CampaignInfo(campaign_id=campaign_id)
                
                MeetingTouchpoint.objects.create(
                    meeting_id=str(uuid.uuid4()),
                    contact_id=contact_id_instance,
                    campaign_id=campaign_id_instance,
                    date=timestamp,
                    pmeeting_status='MANUAL',
                    description=body_data
                )
            elif payload['type']=='Notes':
                contact_id_instance = ContactInfo(contact_id=contact_id)
                campaign_id_instance = CampaignInfo(campaign_id=campaign_id)
                
                Note.objects.create(
                    notes_id=str(uuid.uuid4()),
                    contact_id=contact_id_instance,
                    campaign_id=campaign_id_instance,
                    date=timestamp,
                    subject='MANUAL',
                    description=body_data
                )
            
            return Response(data={'status':'Success', 'message':"Data stored in database"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Data not stored in database."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetCustomerInfo(APIView):
    def get(self,request,customer_id):
        try:
            # payload = json.loads(request.body.decode('utf-8'))
            # payload={
            #     'customer_id':'005f851f-7524-4de8-a946-8b1a318bebac',
            # }
            # print(customer_id)

            # customer_id=payload['customer_id']
            customer=CustomerInfo.objects.filter(customer_id=customer_id).values('customer_name','division','region','number_people')[0]
            # print(customer)
            contact=ContactInfo.objects.filter(customer_id=customer_id).values('business_email_id','mobile_number')[0]

            json_object={
                'customer_name':customer['customer_name'],
                'division':customer['division'],
                'region':customer['region'],
                'number_people':customer['number_people'],
                'business_email_id':contact['business_email_id'],
                # 'business_email_id':'contact.larry@gmail.com',
                'mobile_number':contact['mobile_number'],
                # 'mobile_number':"+91-9356747894",
                'customer_descryption':'This is a description of the customer',
                'customer_followers':1000
            }
            return Response(data={'status':'Success', 'json':json_object}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Data not stored in database."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetHistory(APIView):
    def get(self,request,customer_id):
        try: 

            # payload={
            #     'customer_id':'591c7822-814e-4ed3-ac22-214741051dea',
            # }
            # customer_id=payload['customer_id']
            data_array=[]
            contacts=ContactInfo.objects.filter(customer_id=customer_id).values('contact_id')
            # print(contacts, "contacts")
            for contact in contacts:
                #linkedIn
                # print("mai yha hu")
                message_recieved=LinkedInTouchPoints.objects.filter(tp_type='MESSAGE RECIEVED',contact_id=contact['contact_id']).values('date','contact_id','campaign_id')
                for message in message_recieved:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"linkedIn",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"MESSAGE RECIEVED",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date()),
                            "time":str(date_time.time())
                        }
                    )
                
                message_sent=LinkedInTouchPoints.objects.filter(tp_type='MESSAGE SENT',contact_id=contact['contact_id']).values('date','contact_id','campaign_id')
                for message in message_sent:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"linkedIn",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"MESSAGE SENT",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date()),
                            "time":str(date_time.time())

                        }
                    )

                manual_message_sent=LinkedInTouchPoints.objects.filter(tp_type='MANUAL',contact_id=contact['contact_id']).values('date','contact_id','campaign_id')
                for message in manual_message_sent:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"linkedIn",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"MANUAL",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date()),
                            "time":str(date_time.time())

                        }
                    )

                #email
                #delivered
                delivered_mail=EmailTouchPoints.objects.filter(etype='DELIVERED',contact_id=contact['contact_id']).values('date','contact_id','campaign_id')
                # print(delivered_mail, "delivered email")
                for message in delivered_mail:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"email",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"DELIVERED",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date()),
                            "time":str(date_time.time())
                        }
                    )
                    
                
                #responded
                responded_mail=EmailTouchPoints.objects.filter(etype='RESPONDED',contact_id=contact['contact_id']).values('date','contact_id','campaign_id')
                for message in responded_mail:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"email",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"RESPONDED",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date()),
                            "time":str(date_time.time())
                        }
                    )

                manual_mail=EmailTouchPoints.objects.filter(etype='MANUAL',contact_id=contact['contact_id']).values('date','contact_id','campaign_id')
                for message in manual_mail:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"email",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"MANUAL",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date()),
                            "time":str(date_time.time())
                        }
                    )

                

                #calls 
                #responded 
                responded_call=PhoneTouchPoints.objects.filter(pstatus='RESPONDED',contact_id=contact['contact_id']).values('date','contact_id','campaign_id')
                for message in responded_call:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"call",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"RESPONDED",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date()),
                            "time":str(date_time.time())
                        }
                    )

                #not responded
                not_responded_call=PhoneTouchPoints.objects.filter(pstatus='NOT RESPONDED',contact_id=contact['contact_id']).values('date','contact_id','campaign_id')
                for message in not_responded_call:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"call",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"NOT RESPONDED",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date()),
                            "time":str(date_time.time())
                        }
                    )

                #manual data
                manual_call=PhoneTouchPoints.objects.filter(pstatus='MANUAL',contact_id=contact['contact_id']).values('date','contact_id','campaign_id')
                for message in manual_call:
                    contact_id=message['contact_id']
                    campaign_id=message['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(message['date']))
                    data_array.append(
                        {
                            "type":"call",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"MANUAL",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date()),
                            "time":str(date_time.time())
                        }
                    )

                #meetings 
                #scheduled
                scheduled_meetings=MeetingTouchpoint.objects.filter(pmeeting_status='MEETING SCHEDULED',contact_id=contact['contact_id']).values('date','contact_id','campaign_id')
                # print(scheduled_meetings)
                for meeting in scheduled_meetings:
                    contact_id=meeting['contact_id']
                    campaign_id=meeting['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(meeting['date']))
                    data_array.append(
                        {
                            "type":"meeting",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"MANUAL",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date()),
                            "time":str(date_time.time())
                        }
                    )

                #notes
                notes=Note.objects.filter(contact_id=contact['contact_id']).values('date','contact_id','campaign_id')
                # print(notes)
                for note in notes:
                    contact_id=note['contact_id']
                    campaign_id=note['campaign_id']
                    contact_name=ContactInfo.objects.filter(contact_id=contact_id).values('first_name','last_name')
                    campaign_name=CampaignInfo.objects.filter(campaign_id=campaign_id).values('campaign_name')
                    date_time=datetime.fromtimestamp(int(note['date']))
                    data_array.append(
                        {
                            "type":"note",
                            "contactName":contact_name[0]['first_name']+" "+contact_name[0]['last_name'],
                            "status":"MANUAL",
                            "campaign":campaign_name[0]['campaign_name'],
                            "date":str(date_time.date()),
                            "time":str(date_time.time())
                        }
                    )

            # print(data_array)

            map={}
            for data in data_array:
                if data['date'] in map:
                    map[data['date']].append({
                        'type':data['type'],
                        'contactName':data['contactName'],
                        'status':data['status'],
                        'campaign':data['campaign'],
                        "time":data['time']
                    })
                else:
                    map[data['date']]=[{
                        'type':data['type'],
                        'contactName':data['contactName'],
                        'status':data['status'],
                        'campaign':data['campaign'],
                        "time":data['time']
                    }]

            arr=[]
            # print(map)
            for (key,value) in map.items():
                arr.append({
                    "date":key,
                    "actions":value

                })
        

            return Response(data={'status':'Success', 'json':arr}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Not able to get history"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContactCorrection(APIView):
    def get(self, request):
        try:
            user_type=request.headers['Scope']
            if user_type=="User":
                userId = request.headers['Userid']
                print(userId)
                campaigns = CampaignSalesPersonMappingInfo.objects.filter(salesperson_id=userId).values('campaign_id')
                json_data=[]
                for campaign in campaigns:
                    contacts=CampaignContactMappingInfo.objects.filter(campaign_id=campaign['campaign_id']).values('contact_id')
                    for contact in contacts:
                        contacts = ContactInfo.objects.filter(contact_id=contact['contact_id']).values('contact_id','customer_id','first_name','last_name','linkedin_id_url','mobile_number','business_email_id','zoominfo_scraping_status')
                        for contact in contacts:
                            customer_data=CustomerInfo.objects.filter(customer_id=contact['customer_id']).values('customer_name')
                            if contact['zoominfo_scraping_status'] is None:
                                json_data.append({
                                    "contactId":contact['contact_id'],
                                    "contactName":contact['first_name']+" "+contact['last_name'],
                                    "companyName":customer_data[0]['customer_name'],
                                    "linkedInId":contact['linkedin_id_url'],
                                    "phone":contact['mobile_number'],
                                    "email":contact['business_email_id'],
                                    "incorrect":[]
                                })
                            elif int(contact['zoominfo_scraping_status'])==4: 
                                json_data.append({
                                    "contactId":contact['contact_id'],
                                    "contactName":contact['first_name']+" "+contact['last_name'],
                                    "companyName":customer_data[0]['customer_name'],
                                    "linkedInId":contact['linkedin_id_url'],
                                    "phone":contact['mobile_number'],
                                    "email":contact['business_email_id'],
                                    "incorrect":['email']
                                })
                            elif int(contact['zoominfo_scraping_status'])==3:
                                json_data.append({
                                    "contactId":contact['contact_id'],
                                    "contactName":contact['first_name']+" "+contact['last_name'],
                                    "companyName":customer_data[0]['customer_name'],
                                    "linkedInId":contact['linkedin_id_url'],
                                    "phone":contact['mobile_number'],
                                    "email":contact['business_email_id'],
                                    "incorrect":['email','phone']
                                })

                return Response(data={'status':'Success', 'json':json_data}, status=status.HTTP_200_OK)
            elif user_type=="Admin":
                contacts = ContactInfo.objects.all().values('contact_id','customer_id','first_name','last_name','linkedin_id_url','mobile_number','business_email_id','zoominfo_scraping_status')
                json_data=[]
                for contact in contacts:
                    customer_data=CustomerInfo.objects.filter(customer_id=contact['customer_id']).values('customer_name')
                    if contact['zoominfo_scraping_status'] is None:
                        json_data.append({
                            "contactId":contact['contact_id'],
                            "contactName":contact['first_name']+" "+contact['last_name'],
                            "companyName":customer_data[0]['customer_name'],
                            "linkedInId":contact['linkedin_id_url'],
                            "phone":contact['mobile_number'],
                            "email":contact['business_email_id'],
                            "incorrect":[]
                        })
                    elif int(contact['zoominfo_scraping_status'])==4: 
                        json_data.append({
                            "contactId":contact['contact_id'],
                            "contactName":contact['first_name']+" "+contact['last_name'],
                            "companyName":customer_data[0]['customer_name'],
                            "linkedInId":contact['linkedin_id_url'],
                            "phone":contact['mobile_number'],
                            "email":contact['business_email_id'],
                            "incorrect":['email']
                        })
                    elif int(contact['zoominfo_scraping_status'])==3:
                        json_data.append({
                            "contactId":contact['contact_id'],
                            "contactName":contact['first_name']+" "+contact['last_name'],
                            "companyName":customer_data[0]['customer_name'],
                            "linkedInId":contact['linkedin_id_url'],
                            "phone":contact['mobile_number'],
                            "email":contact['business_email_id'],
                            "incorrect":['email','phone']
                        })
     
                return Response(data={'status':'Success', 'json':json_data}, status=status.HTTP_200_OK)
            else:
                return Response("Bad Request.Invalid User type", status=status.HTTP_200_OK)
                    
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data={'status':'Failed', 'message':"Test failed. Credentials are incorrect."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self,request):
        payload = json.loads(request.body.decode('utf-8'))
        # contact_id=payload['contact_id']
        print(payload)
        data=payload['data']
        if "email" in data and "phone" in data: 
            ContactInfo.objects.filter(contact_id=payload['contact_id']).update(business_email_id=data['email'],mobile_number=data['phone'])
        elif "email" in data:
            ContactInfo.objects.filter(contact_id=payload['contact_id']).update(business_email_id=data['email'])
        elif "phone" in data:
            ContactInfo.objects.filter(contact_id=payload['contact_id']).update(mobile_number=data['phone'])
        
        return Response(data={'status':'Success', 'Message':'Contact Updated succesfully'}, status=status.HTTP_200_OK)


# microservice for history retrieval
def get_dripify_people(campaign_uuid):
    # campaign_uuid="7d5406c8-7986-4223-b29a-de5ea1ed486e"
    # Assuming campaign_uuid is a string, directly use it in filtering
    dripify_profiles = LinkedInTouchPoints.objects.filter(
        dripify_status="changed",
        campaign_id=campaign_uuid  # Use the string directly for filtering
    ).select_related('contact_id')  # Use 'contactinfo' for related object

    dripify_contacts = [profile.contact_id for profile in dripify_profiles if profile.contact_id]

    # Access first_name and last_name from ContactInfo objects
    dripify_contacts_names = [
        f"{contact.first_name} {contact.last_name}" for contact in dripify_contacts
    ]

    print(dripify_contacts_names)

    return dripify_contacts_names
        

def dripify_history(driver, campaign_uuid):
# def dripify_history():        
    # options = Options()
    # # options.add_argument("--headless")
    # options.add_argument(
    #     'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    # options.add_argument('window-size=1200x600')
    # driver = webdriver.Chrome(options=options)
    # driver.maximize_window()
    # wait = WebDriverWait(driver, 120)
    # driver.get('https://app.dripify.io/')
    # time.sleep(1)
    # # window_handles = driver.window_handles
    # # second_window_handle = window_handles[1]
    # # driver.switch_to.window(second_window_handle)
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
    # driver.find_element(By.ID, "campaigns-link").click()
    # driver.implicitly_wait(180)
    # # driver.find_element(By.XPATH, "//span[text()='New campaign']//parent::a").is_displayed()
    # # time.sleep(2)
    # driver.find_element(By.XPATH, "//a[text()=' Deb_Full Flow_MFG_2_GetLeads_500-1000 ']").is_displayed()
    # time.sleep(2)
    # driver.find_element(By.XPATH, "//a[text()=' Deb_Full Flow_MFG_2_GetLeads_500-1000 ']").click()
    # driver.implicitly_wait(180)
    # driver.find_element(By.XPATH, "//article[@class='leads-pack']").is_displayed()
    # time.sleep(2)
    # driver.save_screenshot('error1.png')
    # all_leads = driver.find_element(By.XPATH,
    #                                 "//div[contains(text(),' All leads ')]//preceding-sibling::div[@class='campaign-value__main']").text
    # print(all_leads, " all leads")
    # completed_leads = driver.find_element(By.XPATH,
    #                                       "//div[contains(text(),' Completed all steps ')]//preceding-sibling::div[@class='campaign-value__main']").text
    # print(completed_leads, " completed leads")
    # leads_xpath_size = len(driver.find_elements(By.XPATH,
    #                                             "//article[@class='leads-pack']//a[contains(@class,'leads-pack__name leads-pack__name--link')]"))
    try:
        # if leads_xpath_size > 0:
        #     driver.find_element(By.XPATH,
        #                         "//article[@class='leads-pack']//a[contains(@class,'leads-pack__name leads-pack__name--link')]").click()
        # window_handles = driver.window_handles
        # first_window_handle = window_handles[0]
        # driver.switch_to.window(first_window_handle)
        driver.find_element(By.XPATH, "/html/body/div[1]/div[1]/main/div[1]/div[2]/div[2]/section/div[2]/ul/li/article/div/div[1]/a").click()
        time.sleep(5)
        print("dripify history  starting")
        driver.implicitly_wait(120)
        driver.find_element(By.XPATH, "//button[contains(text(),'Export')]").is_displayed()
        print("inside export button page")
        time.sleep(2)
        driver.find_element(By.XPATH, "//button[@id='leadsView']//parent::div//*[local-name()='svg']").click()
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[text()='10']").click()
        time.sleep(3)
        spinner_flag = True
        while spinner_flag:
            driver.implicitly_wait(1)
            size_spinner = len(driver.find_elements(By.XPATH, "//div[@class='inline-spinner']"))
            if size_spinner == 0:
                spinner_flag = False

        
        total_pages_array = driver.find_elements(By.XPATH,
                                                 "//ul[@class='pagination']//li[@class='pagination__item']//button")
        total_papges = total_pages_array[-1].text
        print(total_papges)
        total_papges=  1
        
        peoples=get_dripify_people(campaign_uuid)
        time.sleep(2)
        for i in range(len(peoples)):
            time.sleep(30)
            driver.find_element(By.XPATH, "//input[@class='field__input']").is_displayed()
            element = driver.find_element(By.XPATH, "//input[@class='field__input']")

            element.send_keys(peoples[i])
            time.sleep(3)
            # Pages Level
            for i in range(int(total_papges)):
                # print(i, " ", i + 1)
                # driver.implicitly_wait(20)
                # driver.find_element(By.XPATH,
                #                     "//ul[@class='pagination']//li[contains(@class,'pagination__item')]//button[text()=' " + str(
                #                         i + 1) + " ']").is_displayed()
                # driver.find_element(By.XPATH,
                #                     "//ul[@class='pagination']//li[contains(@class,'pagination__item')]//button[text()=' " + str(
                #                         i + 1) + " ']").click()
                time.sleep(2)
                spinner_flag_leads = True
                while spinner_flag_leads:
                    driver.implicitly_wait(1)
                    size_spinner = len(driver.find_elements(By.XPATH, "//div[@class='inline-spinner']"))
                    if size_spinner == 0:
                        spinner_flag_leads = False
                #hk-make a note
                size_of_leads = len(driver.find_elements(By.XPATH,
                                                        "//ul[@aria-label='List of leads']//li[@aria-label='Lead']//a"))
                print(size_of_leads)
                # Leads level
                for j in range(int(size_of_leads)):
                    driver.implicitly_wait(60)
                    driver.find_elements(By.XPATH, "//ul[@aria-label='List of leads']//li[@aria-label='Lead']//a")[
                        j].is_displayed()
                    time.sleep(1)
                    print(
                        driver.find_elements(By.XPATH, "//ul[@aria-label='List of leads']//li[@aria-label='Lead']//a")[
                            j].text, " text name")
                    if j == 0:
                        driver.execute_script("arguments[0].scrollIntoView();",
                                            driver.find_element(By.XPATH, "//div[@class='leads__head']"))

                    else:
                        driver.execute_script("arguments[0].scrollIntoView();", driver.find_elements(By.XPATH,
                                                                                                    "//ul[@aria-label='List of leads']//li[@aria-label='Lead']//a")[
                            j - 1])

                    driver.find_elements(By.XPATH, "//ul[@aria-label='List of leads']//li[@aria-label='Lead']//a")[
                        j].click()
                    spinner_flag_inside_leads = True
                    while spinner_flag_inside_leads:
                        driver.implicitly_wait(1)
                        size_spinner = len(driver.find_elements(By.XPATH, "//div[@class='inline-spinner']"))
                        if size_spinner == 0:
                            spinner_flag_inside_leads = False
                    time.sleep(1)
                    driver.implicitly_wait(3)
                    size_inativity = len(driver.find_elements(By.XPATH, "//div[@class='activity-timeline-empty']"))
                    linkedin_url = driver.find_element(By.XPATH, "//div[@class='lead-info__avatar']//a").get_attribute(
                        'href')
                    print(linkedin_url, " linkedin url")
                    contact_info = ContactInfo.objects.get(linkedin_url_encrypted=linkedin_url[:-1])
                    contact_uuid = contact_info.contact_id
                    if size_inativity == 0:
                        size_interactions = len(
                            driver.find_elements(By.XPATH, "//ul[@role='feed']//li[@class='activity-timeline-day']"))
                        # Go through each interaction
                        for k in range(size_interactions):
                            # Get the date when the actions are done
                            date = driver.find_elements(By.XPATH,
                                                        "//ul[@role='feed']//li[@class='activity-timeline-day']//h4[contains(@class,'activity-timeline-day__date')]")[
                                k].text
                            print(date, " date")
                            convos_per_day_size = len(driver.find_elements(By.XPATH,
                                                                        "//ul[@role='feed']//time[contains(text(),'" + date + "')]//ancestor::li[@class='activity-timeline-day']//ul//li"))
                            # Go through each sub interaction on the same date
                            for l in range(convos_per_day_size):
                                # Get the time stamp for each convo
                                time_stamp = driver.find_elements(By.XPATH,
                                                                "//ul[@role='feed']//time[contains(text(),'" + date + "')]//ancestor::li[@class='activity-timeline-day']//ul//li//time")[
                                    l].text
                                print(time_stamp, " time")
                                # get the information about the update
                                message = driver.find_elements(By.XPATH,
                                                            "//ul[@role='feed']//time[contains(text(),'" + date + "')]//ancestor::li[@class='activity-timeline-day']//ul//li//div")[
                                    l].text
                                print(message, " message")

                                # Assign the Template Type
                                template_type = filter_templete_type(message)

                                # convert data, time into time stamp
                                date_object = datetime.strptime(f"{date},{time_stamp}", "%b %d, %Y,%H:%M")

                                # Convert to timestamp
                                timestamp = int(date_object.timestamp())

                                contact_uuid_instance = ContactInfo(contact_id=contact_uuid)
                                campaign_id_instance = CampaignInfo(campaign_id=campaign_uuid)
                                print(contact_uuid_instance,"contact uuid")
                                print(campaign_id_instance,"campaign_id_instance")
                                
                                # Check if the touchpoint already exists
                                existing_touchpoint = LinkedInTouchPoints.objects.filter(
                                    contact_id=contact_uuid_instance,
                                    campaign_id=campaign_id_instance,
                                    date=str(timestamp)
                                ).exists()
                                existing_touchpoint=False

                                linkedin_template_id="528be2fb-24bf-47cd-84dc-d65b9ee5c254"
                                linkedin_template_instance=LinkedInTouchPoints(linkedin_template_id=linkedin_template_id)
                                if not existing_touchpoint:
                                    # Insert Data into LinkedIn Touchpoints table
                                    LinkedInTouchPoints.objects.create(
                                        ltp_id=str(uuid.uuid4()),
                                        tp_type=template_type,
                                        linkedin_template_id=linkedin_template_id,
                                        contact_id=contact_uuid_instance,
                                        campaign_id=campaign_id_instance,
                                        date=timestamp,
                                        subject=message,
                                        dripify_status='unchanged'
                                        # lstatus=request.data['status']
                                    )

                                    print("saved in linkedin touchpoints")

                        # Go through the mesaaging convo
                        time.sleep(1)
                        driver.implicitly_wait(1)
                        converstation_status = len(driver.find_elements(By.XPATH,
                                                                        "//main//button[contains(@class,'btn--base btn--to-icon-on-fablet')]"))
                        if converstation_status == 0:
                            driver.find_element(By.XPATH, "//main//a[contains(@href,'/inbox')]").click()
                            driver.implicitly_wait(120)
                            driver.find_element(By.XPATH,
                                                "//div[contains(@aria-label,'Outcome message')]").is_displayed()
                            time.sleep(1)

                            size_no_of_messages = len(
                                driver.find_elements(By.XPATH, "//div[@role='feed']//div[contains(@role,'article')]"))
                            # print(size_no_of_messages, " total no of messages")
                            last_updated_date = ""
                            for messages in range(size_no_of_messages):
                                # Date of the Message
                                # check date is present or not
                                driver.implicitly_wait(2)
                                size_date = len(driver.find_elements(By.XPATH,
                                                                    "//div[@role='feed']//div[contains(@aria-posinset,'" + str(
                                                                        messages + 1) + "')]//time[@class='msg__new-day']"))
                                if size_date > 0:
                                    date = driver.find_element(By.XPATH,
                                                            "//div[@role='feed']//div[contains(@aria-posinset,'" + str(
                                                                messages + 1) + "')]//time[@class='msg__new-day']").text
                                    last_updated_date = date

                                # Message
                                message = driver.find_elements(By.XPATH,
                                                            "//div[@role='feed']//div[contains(@role,'article')]//div[@class='msg__content']//p")[
                                    messages].text

                                # Timestamp
                                timestamp = driver.find_elements(By.XPATH,
                                                                "//div[@role='feed']//div[contains(@role,'article')]//div[@class='msg__content']//time")[
                                    messages].text
                                time_24hr = datetime.strptime(timestamp, "%I:%M %p").strftime("%H:%M")
                                print(time_24hr, " time")
                                # Message Type
                                type = driver.find_elements(By.XPATH,
                                                            "//div[@role='feed']//div[contains(@role,'article')]")[
                                    messages].get_attribute('aria-label')
                                #
                                date_object = datetime.strptime(f"{last_updated_date},{time_24hr}", "%a %b %d %Y,%H:%M")

                                # Convert to timestamp
                                timestamp_message = int(date_object.timestamp())

                                # mapping msgs to the above subjects

                                # Check if the record exists with the specified filter condition

                                existing_touchpoint = LinkedInTouchPoints.objects.filter(
                                    contact_id=contact_uuid,
                                    campaign_id=campaign_uuid,
                                    date=str(timestamp_message),
                                    body=''
                                )

                                if existing_touchpoint:
                                    LinkedInTouchPoints.objects.filter(contact_id=contact_uuid,
                                                                    campaign_id=campaign_uuid,
                                                                    date=str(timestamp_message)).update(
                                        body=message,dripify_status='unchanged')

                                print(type, " message type")
                                print(last_updated_date, " date")
                                print(message, " message")
                                print(timestamp, "  time")

                            driver.back()
                            time.sleep(3)
                        driver.back()
                        time.sleep(5)
                        print("------------------------------------------")
                    else:
                        LinkedInTouchPoints.objects.filter(contact_id=contact_uuid,campaign_id=campaign_uuid).update(dripify_status='unchanged')
                        print("no update")
                        driver.back()
                        time.sleep(5)

    except Exception as e:
        driver.save_screenshot('error.png')
        logger.info(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_tb.tb_lineno)
        

def update_campaign_status_for_history(campaign_id, driver):
    try:
        campaign = CampaignInfo.objects.filter(campaign_id=campaign_id).values().first()
        print(campaign, "camping in update function")
        print(campaign['campaign_name'], " campaign name")
        driver.save_screenshot(os.getcwd() + '/error.png')
        driver.find_element(By.XPATH, "//a[text()=' " + campaign['campaign_name'] + " ']").is_displayed()
        time.sleep(2)
        driver.find_element(By.XPATH, "//a[text()=' " + campaign['campaign_name'] + " ']").click()
        driver.implicitly_wait(180)
        driver.find_element(By.XPATH, "//article[@class='leads-pack']").is_displayed()
        time.sleep(2)
        driver.save_screenshot('error1.png')
        all_leads = driver.find_element(By.XPATH,
                                        "//div[contains(text(),' All leads ')]//preceding-sibling::div[@class='campaign-value__main']").text
        print(all_leads, " all leads")
        completed_leads = driver.find_element(By.XPATH,
                                              "//div[contains(text(),' Completed all steps ')]//preceding-sibling::div[@class='campaign-value__main']").text
        print(completed_leads, " completed leads")
        leads_xpath_size = len(driver.find_elements(By.XPATH,
                                                    "//article[@class='leads-pack']//a[contains(@class,'leads-pack__name leads-pack__name--link')]"))
        if leads_xpath_size > 0:
            driver.find_element(By.XPATH,
                                "//article[@class='leads-pack']//a[contains(@class,'leads-pack__name leads-pack__name--link')]").click()
            driver.implicitly_wait(120)
            dripify_history(driver, campaign_id)
            # zoominfo(driver)

    except Exception as e:
        driver.save_screenshot('error2.png')
        logger.info(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_tb.tb_lineno)
        return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def automate_salesperson_login_for_history(salesperson, driver):
    try:
        # Log in to Dripify
        # driver.get('https://app.dripify.io/')
        # window_handles = driver.window_handles
        # second_window_handle = window_handles[1]
        # driver.switch_to.window(second_window_handle)
        driver.get("https://app.dripify.io/")
        print(salesperson.username, " username")
        print(salesperson.password, " password")
        driver.implicitly_wait(180)
        driver.find_element(By.ID, "email").is_displayed()
        driver.find_element(By.ID, "email").send_keys(salesperson.username)
        time.sleep(1)
        driver.find_element(By.ID, "password").send_keys(salesperson.password)
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[@type='submit']").is_enabled()
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        driver.implicitly_wait(180)
        driver.find_element(By.XPATH, "//h2[text()='Statistics']").is_displayed()
        time.sleep(2)
        print("inside dripify")
        # Iterate over campaigns for the salesperson
        campaign_mappings = list(
            CampaignSalesPersonMappingInfo.objects.filter(salesperson_id=salesperson.saels_person_id).values())
        print(campaign_mappings, " mapping of campaisgns")
        

        for mapping in campaign_mappings:
            # driver.save_screenshot('error2.png')
            driver.find_element(By.ID, "campaigns-link").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//span[text()='New campaign']//parent::a").is_displayed()
            time.sleep(2)
            campaign = CampaignInfo.objects.filter(campaign_id=mapping['campaign_id_id']).values().first()
            if campaign['campaign_status'] != 'Completed':
                print(f"Processing campaign {campaign['campaign_name']} for {salesperson.username}")
                # Update the campaign status
                update_campaign_status_for_history(campaign['campaign_id'], driver)
            else:
                print(f"Skipping completed campaign {campaign.campaign_name} for {salesperson.username}")

    except Exception as e:

        logger.info(str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(exc_type, exc_tb.tb_lineno)
        return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        # Close the browser window
        driver.quit()


def get_salespersons_and_campaigns_for_history():
    salespersons_and_campaigns = {}

    # Assuming you have a ForeignKey relationship between SalesPersonInfo and CampaignInfo
    salespersons = SalesPersonDetails.objects.filter(user_level='User',service='Dripify')
    print(salespersons, "salespersons")

    for salesperson in salespersons:
        campaigns=CampaignSalesPersonMappingInfo.objects.filter(salesperson_id=salesperson.saels_person_id).values('campaign_id')
        # campaigns = salesperson.campaignsalespersonmappinginfo_set.all().select_related('campaign_id')
        salespersons_and_campaigns[salesperson] = campaigns

    print(salespersons_and_campaigns, "salespersons_and_campaigns")
    return salespersons_and_campaigns


def dripify_history_retrieval():
    print("inside dripify history")
    dripify_flag = False
    last_status = CronJobInfo.objects.filter(model_name='DRIPIFY HISTORY').order_by('-start_ts').first()
    if last_status==None or last_status.status != 'In Progress':
        dripify_flag = True
        job_id = str(uuid.uuid4())
        CronJobInfo.objects.create(
            job_uuid=job_id,
            model_name='DRIPIFY HISTORY',
            start_ts=int(datetime.now().timestamp()),
            end_ts=None,
            status='In Progress',
            remarks=None
        )
    else:
        print("in progress so flag is false")
    if dripify_flag:
        try:
            salespersons_and_campaigns = get_salespersons_and_campaigns_for_history()
            # print(salespersons_and_campaigns, " salespersons and campaigns")
            for salesperson, campaigns in salespersons_and_campaigns.items():
                # try:
                options = Options()
                # options.add_argument("--headless=chrome")
                options.add_argument(
                    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
                options.add_argument('window-size=1200x600')
                options.add_experimental_option("prefs", {
                    "download.default_directory": "/home/vassar/Downloads/",
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "plugins.always_open_pdf_externally": True
                })
                options.add_argument("--disable-popup-blocking")
                driver = webdriver.Chrome(options=options)
                # time.sleep(2)
                driver.maximize_window()
                print(salesperson, " salesperson")
                # open_gmail(driver)
                automate_salesperson_login_for_history(salesperson, driver)
                driver.quit()
                # except ObjectDoesNotExist:
                #     print(f"Salesperson {salesperson.salesperson_name} not found in the database.")
                # except Exception as e:
                #     print(f"Error processing salesperson {salesperson.salesperson_name}: {e}")

                time.sleep(5)

            CronJobInfo.objects.filter(job_uuid=job_id).update(
                end_ts=int(datetime.now().timestamp()),
                status='SUCCESS'
            )

            # return Response("success", status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            CronJobInfo.objects.filter(job_uuid=job_id).update(
                end_ts=int(datetime.now().timestamp()),
                status='FAILURE',
                remarks=str(e)
            )

            # return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # time.sleep(3000)


#microservice for creating a new campaign dynamically
def call_dripify(dripify_username, dripify_password, campaign_name, campaign_url,campaign_type,userid,dripify_template_name):
        try:
            # print(request.data['list_name'], " listname")
            options = Options()
            temp_path="//h2[text()='"+dripify_template_name+"']"
            # options.add_argument("--headless")
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            options.add_argument('window-size=1200x600')
            driver = webdriver.Chrome(options=options)
            driver.maximize_window()
            driver.get("https://app.dripify.io/")
            # time.sleep(3000)
            driver.implicitly_wait(180)
            driver.find_element(By.ID, "email").is_displayed()
            driver.find_element(By.ID, "email").send_keys(dripify_username)
            time.sleep(1)
            driver.find_element(By.ID, "password").send_keys(dripify_password)
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[@type='submit']").is_enabled()
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//h2[text()='Statistics']").is_displayed()
            time.sleep(2)
            driver.find_element(By.ID, "campaigns-link").click()
            driver.implicitly_wait(180)
            time.sleep(5)
            driver.find_element(By.XPATH, "//span[text()='New campaign']//parent::a").is_displayed()
            time.sleep(2)
            driver.find_element(By.XPATH, "//span[text()='New campaign']//parent::a").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//button[text()=' Add leads ']").is_displayed()
            time.sleep(2)
            driver.find_element(By.XPATH, "//button[text()=' Add leads ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.ID, "leadsPackName").is_displayed()
            time.sleep(1)
            driver.find_element(By.ID, "leadsPackName").send_keys(campaign_name)
            file_path = "output_file.csv"
            no_of_profiles_found = "1"
            if campaign_type == 'Upload CSV File':
                driver.find_element(By.XPATH, "//a[text()='Upload CSV file']").click()
                driver.implicitly_wait(180)
                driver.find_element(By.XPATH, "//input[@type='file']").is_displayed()
                time.sleep(2)
                driver.find_element(By.XPATH, "//input[@type='file']").send_keys(
                    os.getcwd() + "/output_file.csv")
                no_of_profiles_found = driver.find_element(By.XPATH, "//p[text()=' LinkedIn profiles found: ']//b").text
            else:
                driver.find_element(By.ID, "LinkedInSearch").send_keys(campaign_url)
                time.sleep(10)
                no_of_profiles_found = driver.find_element(By.XPATH, "//div[@class='leads-count-found' and contains(text(), 'LinkedIn profiles found:')]//b").text
                no_of_profiles_found=no_of_profiles_found.replace(" ","")
                time.sleep(2)

                # Clear the input field
                for i in range(3):
                    driver.find_element(By.XPATH, "//input[@id='leadsCount']").send_keys(Keys.BACK_SPACE)
                time.sleep(2)
                # Send keys to the input field
                driver.find_element(By.XPATH, "//input[@id='leadsCount']").send_keys(no_of_profiles_found)
                
            time.sleep(2)
            print(no_of_profiles_found, " profiles found")
            driver.find_element(By.XPATH, "//button[text()=' Create a list ']").is_enabled()
            driver.find_element(By.XPATH, "//button[text()=' Create a list ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//button[text()=' Next ']").is_displayed()
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[text()=' Next ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//button[text()=' Saved Templates ']").is_displayed()
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[text()=' Saved Templates ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, temp_path).is_displayed()
            time.sleep(1)
            driver.find_element(By.XPATH, temp_path).click()
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[text()=' Select template ']").is_enabled()
            driver.find_element(By.XPATH, "//button[text()=' Select template ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//button[text()=' Next ']").is_displayed()
            time.sleep(1)
            driver.find_element(By.XPATH, "//button[text()=' Next ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.ID, "Name").is_displayed()
            driver.find_element(By.ID, "Name").send_keys(campaign_name)
            time.sleep(2)
            driver.find_element(By.ID, "saveCampaignBtn").is_enabled()
            driver.find_element(By.ID, "saveCampaignBtn").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//a[text()=' Back to campaigns ']").is_displayed()
            time.sleep(1)
            driver.find_element(By.XPATH, "//a[text()=' Back to campaigns ']").click()
            driver.implicitly_wait(180)
            driver.find_element(By.XPATH, "//a[text()=' " + campaign_name + " ']").is_displayed()
            time.sleep(2)
            campaign_creation_status = "Created"
            # campaign_id = str(uuid.uuid4())
            driver.quit()
            # timestamp = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
            # no_of_profiles_found="300"
            print(userid,
                campaign_name,
                campaign_creation_status,
                no_of_profiles_found)
            
            #create nahi krna update krna hai...
            CampaignInfo.objects.filter(
                campaign_id=userid,    
            ).update(
                campaign_status=campaign_creation_status,
                no_of_leads=no_of_profiles_found
            )
            


            json_array = []
            json_object = {
                'campaign_name': campaign_name,
                'campaign_status': campaign_creation_status,
                "no_of_users": no_of_profiles_found
            }


            json_array.append(json_object)
            campaign_creation_status = "success"
            return Response(json_array, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

def create_campaign_dripify():
    print("inside dripify campaign creation")
    dripify_flag = False
    last_status = CronJobInfo.objects.filter(model_name='DRIPIFY CAMPAIGN CREATION').order_by('-start_ts').first()
    if last_status==None or last_status.status != 'In Progress':
        dripify_flag = True
        job_id = str(uuid.uuid4())
        CronJobInfo.objects.create(
            job_uuid=job_id,
            model_name='DRIPIFY CAMPAIGN CREATION',
            start_ts=int(datetime.now().timestamp()),
            end_ts=None,
            status='In Progress',
            remarks=None
        )
    else:
        print("in progress so flag is false")
    if dripify_flag:
        try:
            pass
            filtered_records = CampaignInfo.objects.filter(campaign_status="Scheduled").values('campaign_id','created_ts','campaign_name','description','attribute_value_pairs')
            print(filtered_records, " filtered records")
            # dates = [datetime.strptime(record['created_ts'], "%m-%d-%Y %H:%M:%S").date() for record['created_ts'] in filtered_records] 
            for record in filtered_records:
                timeStamp = int(int(record['created_ts']) / 1000)  # Convert milliseconds to seconds
                date_of_record = datetime.fromtimestamp(timeStamp).date()
                today_date = date.today()
                print(date_of_record)
                # timeStamp=int(record['created_ts'])/1000
                # date_of_record=datetime.fromtimestamp(timeStamp)
                # today_date = date.today()
                if date_of_record == today_date:
                    salesperson_data=CampaignSalesPersonMappingInfo.objects.filter(campaign_id=record['campaign_id']).values('salesperson_id')
                    print(salesperson_data[0]['salesperson_id'])
                    
                    salesperson_details = SalesPersonDetails.objects.all().values('saels_person_id','username','password','service')
                    print(salesperson_details)

                    sales_person_data={}
                    print(salesperson_data[0]['salesperson_id'])
                    id_salesperson=str(salesperson_data[0]['salesperson_id'])
                    for salesperson in salesperson_details:
                        if salesperson['saels_person_id']==id_salesperson and salesperson['service']=='Dripify':
                            sales_person_data=salesperson

                    print(sales_person_data, " sales person data")
                    
                    call_dripify(sales_person_data['username'], sales_person_data['password'], record['campaign_name'], record['description'],'LinkedIn Search',id_salesperson,record['attribute_value_pairs'])   
                    
                else:
                    print("not scheduled for today.")
                    # print(record['created_ts']," not today")  

            CronJobInfo.objects.filter(job_uuid=job_id).update(
                end_ts=int(datetime.now().timestamp()),
                status='SUCCESS'
            )
        except Exception as e:
            logger.info(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            CronJobInfo.objects.filter(job_uuid=job_id).update(
                end_ts=int(datetime.now().timestamp()),
                status='FAILURE',
                remarks=str(e)
            ) 


