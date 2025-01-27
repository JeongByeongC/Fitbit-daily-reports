#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 11:45:27 2024

@author: jbc0102
"""
import requests, base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys


def automate_code_retrieval(FITBIT_USERNAME, FITBIT_PASSWORD, FITBIT_CLIENT_ID, chrome_options):
    """
    Grabs the initial code from the Fitbit website containing
    the correct scopes.
    :return: the code as a string
    """
    url = "https://www.fitbit.com/oauth2/authorize" \
        "?response_type=code" \
        f"&client_id={FITBIT_CLIENT_ID}" \
        "&redirect_uri=http%3A%2F%2F127.0.0.1%3A8080%2F" \
        "&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight%20oxygen_saturation%20respiratory_rate%20temperature" \
        "&expires_in=604800"
    
    
    
    # //*[@id="ember537"]//*[@id="ember537"]
    # Get URL
    driver = uc.Chrome(version_main=121)
    driver.get(url)
    
    # Complete login form
    WebDriverWait(driver, 80).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='email']")))
    
    numbers_in_email = ''.join(filter(str.isdigit, FITBIT_USERNAME))
    num_list  = ['037', '038', '039', '040', '041', '042', '050', '051', '052', '053', '054', '055',
    '056', '059', '060', '062', '063', '064', '065', '067', '068', '069', '070', '072']
    
    if any(number in numbers_in_email for number in num_list):
        #//*[@id="ember536"]/button/div/span
        google = driver.find_element(By.XPATH, '//*[@id="ember537"]/button')
        google.click()
        WebDriverWait(driver, 80).until(EC.presence_of_element_located((By.XPATH, "//*[@id='identifierId']")))
        username_input = driver.find_element(By.XPATH, "//input[@type='email']")
        username_input.send_keys(FITBIT_USERNAME)
        next_butten = driver.find_element(By.XPATH, "//*[@id='identifierNext']/div/button")
        next_butten.send_keys(Keys.ENTER)
        WebDriverWait(driver, 80).until(EC.presence_of_element_located((By.XPATH, "//*[@id='password']/div[1]/div/div[1]/input")))
        password_input = driver.find_element(By.XPATH, "//*[@id='password']/div[1]/div/div[1]/input")
        password_input.send_keys(FITBIT_PASSWORD)
        next_butten2 = driver.find_element(By.XPATH, "//*[@id='passwordNext']/div/button")
        next_butten2.send_keys(Keys.ENTER)
               
    else:
        username_input = driver.find_element(By.XPATH, "//input[@type='email']")
        password_input = driver.find_element(By.XPATH, "//input[@type='password']")
        submit = driver.find_element(By.XPATH, "//form[@id='loginForm']/div/button")
        username_input.send_keys(FITBIT_USERNAME)
        password_input.send_keys(FITBIT_PASSWORD)
        submit.click()
    # Get code
    WebDriverWait(driver, 80).until(EC.url_contains("127.0.0.1:8080"))
    code = driver.current_url.split("code=")[-1].split("#")[0]
    driver.quit()
    return code

def automate_token_retrieval(code, FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET):
    """
    Using the code from the Fitbit website, retrieves the
    correct set of tokens.
    """
    data = {
        "clientId": FITBIT_CLIENT_ID,
        "grant_type": "authorization_code",
        "redirect_uri": "http://127.0.0.1:8080/",
        "code": code
    }
    basic_token = base64.b64encode(
        f"{FITBIT_CLIENT_ID}:{FITBIT_CLIENT_SECRET}".encode("utf-8")
    ).decode("utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {basic_token}"
    }
    response = requests.post(data=data, headers=headers,
                             url="https://api.fitbit.com/oauth2/token")
    keys = response.json()
    #dotenv.set_key(".env", "FITBIT_ACCESS_TOKEN", keys["access_token"])
    #dotenv.set_key(".env", "FITBIT_REFRESH_TOKEN", keys["refresh_token"])
    #dotenv.set_key(".env", "FITBIT_EXPIRES_AT", str(keys["expires_in"]))
    return keys

def automate_refresh_token(old_keys, FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET):
    data = {"grant_type": "refresh_token",
    "refresh_token": old_keys["refresh_token"]
    }
    basic_token = base64.b64encode(
        f"{FITBIT_CLIENT_ID}:{FITBIT_CLIENT_SECRET}".encode("utf-8")
    ).decode("utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {basic_token}"
    }
    
    response = requests.post(data=data, headers=headers, 
                             url='https://api.fitbit.com/oauth2/token')
    
    new_keys = response.json()
    return new_keys
