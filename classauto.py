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

# Login with username and password
username = driver.find_element(By.XPATH, '//*[@id="username"]')
username.send_keys(os.getenv('COLLEGE_USERNAME'))
password = driver.find_element(By.XPATH, '//*[@id="password"]')
password.send_keys(os.getenv('COLLEGE_PASSWORD'))
password.send_keys(Keys.RETURN)

# Wait for the Duo authentication page to load
WebDriverWait(driver, 2).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="duo_iframe"]'))
)

# Switch to the Duo iframe
duo_iframe = driver.find_element(By.XPATH, '//*[@id="duo_iframe"]')
driver.switch_to.frame(duo_iframe)

# Click on "Enter a Passcode" tab
passcode_tab = WebDriverWait(driver, 1).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="passcode"]'))
)
passcode_tab.click()

# Generate the OTP code
totp = pyotp.TOTP(os.getenv('TOTP_SECRET'))
otp_code = totp.now()

# Enter the OTP code
otp_input = driver.find_element(By.XPATH, '//*[@id="auth_methods"]/fieldset/div[3]/div/input')
otp_input.send_keys('514621')

#clicking on the remember me button
remember_me = driver.find_element(By.XPATH, '//*[@id="login-form"]/div[2]/div/label/input')
remember_me.click()

otp_input.send_keys(Keys.RETURN)

# Save cookies to a file
with open('cookies.pkl', 'wb') as file:
    pickle.dump(driver.get_cookies(), file)

# Wait for Duo authentication to complete
time.sleep(5)  

# Close WebDriver
driver.quit()
