from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import time
from enroller import main_enroller

def check_class_availability(class_number):
    print("Setting up Chrome options...")
    options = webdriver.ChromeOptions()

    print("Initializing WebDriver...")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        print("Navigating to ASU class catalog...")
        string_with_number = "https://catalog.apps.asu.edu/catalog/classes/classlist?campusOrOnlineSelection=A&honors=F&keywords=" + class_number + "&promod=F&searchType=all&term=2251"
        print("Getting the class number with string...")
        driver.get(string_with_number)

        print("Waiting for class information to load...")
        time.sleep(2)  # Check every 2 seconds

        try:
            print("Checking class status...")
            class_status_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='class-results-cell seats']/div[@class='text-nowrap']")))

            # Get the text content of the element
            availability_text = class_status_element.text
            print(f"Availability text: {availability_text}") 
            
            while True:
                # Check if seats are available
                if "0 of" not in availability_text:
                    print("Seats available, sending email...")
                    
                    #if seats available run main enroller from enroller.py
                    main_enroller()
                    print("Ran main enroller")
                    
                    WebDriverWait(driver, 20)
                    break
                else:
                    print("No seats available, waiting 2 seconds...")
                    time.sleep(2)
                    # Refresh the page to check again
                    driver.refresh()
                    class_status_element = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='class-results-cell seats']/div[@class='text-nowrap']")))
                    availability_text = class_status_element.text
                    print(f"Class {class_number} status: {availability_text}")

        except Exception as e:
            print(f"Could not find status for class {class_number}: {e}")

    finally:
        print("Quitting WebDriver...")
        driver.quit()

if __name__ == "__main__":
    class_number = ""  # Specify your class number here
    check_class_availability(class_number)