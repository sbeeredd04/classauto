from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyotp
import time
from selenium.webdriver.chrome.options import Options

service = webdriver.chrome.service.Service('/workspaces/classauto/chromedriver-linux64/chromedriver')
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




