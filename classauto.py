import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyotp
import os
import time
from selenium.webdriver.chrome.service import Service

# Setup environment variables (This should be done securely in your OS)
os.environ['COLLEGE_USERNAME'] = 'REDACTED_USERNAME'
os.environ['COLLEGE_PASSWORD'] = 'Sriujjwal@0410'
os.environ['TOTP_SECRET'] = 'GQZDIOJTG4======'

# Initialize WebDriver
service = Service('C:\\Users\\sriuj\\classauto\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service=service)
driver.get('https://webapp4.asu.edu/myasu/')

#credentials
name = 'REDACTED_USERNAME'
password = 'Sriujjwal@0410'

# Login
username = driver.find_element_by_id('username')
username.send_keys(name)
password = driver.find_element_by_id('password')
password.send_keys(password)




