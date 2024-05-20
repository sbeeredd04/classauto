from flask import Flask
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import pickle
from selenium.webdriver.chrome.service import Service

app = Flask(__name__)

def check_class_availability():
    print("Starting class availability check...")  # Log start

    while True:
        try:
            # Initialize WebDriver
            service = Service('C:\\Users\\sriuj\\classauto\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe')
            driver = webdriver.Chrome(service=service)
            driver.get('https://webapp4.asu.edu/myasu/')
            print("WebDriver initialized and navigated to myasu...")  # Log navigation

            # Load cookies
            with open('cookies.pkl', 'rb') as file:
                cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
            print("Cookies loaded...")  # Log cookie loading
            
            # Refresh the page to use the loaded cookies
            driver.refresh()

            # Navigate to the class enrollment page
            driver.get('https://catalog.apps.asu.edu/catalog/classes/classlist?term=2241')
            print("Navigated to class enrollment page...")  # Log navigation
            
            # Check class availability and enroll
            try:
                # Example: Check for the enroll button
                enroll_button = driver.find_element(By.XPATH, 'XPATH_OF_ENROLL_BUTTON')
                if enroll_button:
                    enroll_button.click()
                    print("Successfully enrolled in the class.")
            except Exception as e:
                print("Class not available yet. Exception: ", e)

            # Close the browser
            driver.quit()

            # Wait for some time before checking again (e.g., 5 minutes)
            time.sleep(300)
        except Exception as e:
            print("Exception during checking: ", e)
            driver.quit()

@app.route('/start')
def start_checking():
    thread = threading.Thread(target=check_class_availability)
    thread.start()
    return "Started checking class availability."

if __name__ == '__main__':
    app.run(port=5000, debug=True)  # Debug mode enabled
