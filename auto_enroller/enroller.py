import os
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import sys
import time
import datetime
import pytz  # To handle timezone

# Global variables for credentials, URL, and date/time settings
USERNAME = 'REDACTED_USERNAME'
PASSWORD = 'REDACTED_PASSWORD'
LOGIN_URL = 'https://webapp4.asu.edu/myasu/#!'
TARGET_BUTTON_XPATH = '//*[@id="DERIVED_SSR_FL_SSR_ENROLL_FL"]'
WAIT_DATE = '2024-10-31'  # Format: YYYY-MM-DD
WAIT_TIME = '20:02:00'  # Format: HH:MM:SS (24-hour format, Mountain Standard Time)
KEEP_ALIVE_INTERVAL = 40  # Interval in seconds to keep the session active

# XPath for "Yes" button on the enrollment confirmation pop-up
CONFIRMATION_POPUP_XPATH = '//*[@id="ptModTable_0"]'
CONFIRMATION_YES_BUTTON_XPATH = '//*[@id="#ICYes"]'

class InvitationSender:
    def __init__(self, username, password):
        # Initialize WebDriver and Logger
        self.driver = None
        self.username = username
        self.password = password
        self.init_webdriver()

    def init_webdriver(self):
        """Initialize the Chrome WebDriver."""
        options = ChromeOptions()
        options.add_argument('--user-data-dir={}/userdata'.format(os.getcwd()))  # Use user data if needed
        try:
            self.driver = webdriver.Chrome(options=options)
            logging.info("ChromeDriver initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize ChromeDriver: {e}")
            sys.exit(1)

    def login(self):
        try:
            logging.info("Attempting to open the login page.")
            self.driver.get(LOGIN_URL)
            logging.info(f"Opened URL: {LOGIN_URL}")

            # Attempt login sequence
            logging.info("Waiting for username field to become visible.")
            WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, 'username')))
            self.driver.find_element(By.ID, 'username').send_keys(self.username)
            logging.info("Entered username.")
            
            self.driver.find_element(By.ID, 'password').send_keys(self.password)
            logging.info("Entered password.")

            self.driver.find_element(By.NAME, 'submit').click()
            logging.info("Login credentials submitted.")

            # Check if Duo push confirmation is required
            try:
                logging.info("Checking for Duo push button.")
                duo_button = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, '//button[contains(text(), "Yes, this is my device")]'))
                )
                logging.info("Duo push button found, clicking it.")
                duo_button.click()
            except:
                logging.info("Duo push not required or already authenticated.")

            # Step 1: Attempt to find and click the "Registration" link
            registration_link_xpath = '//*[@id="classes-reg-link"]'
            logging.info("Trying to locate 'Registration' link with different methods.")

            try:
                logging.info("Attempting to find 'Registration' link by ID 'classes-reg-link'.")
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'classes-reg-link'))
                ).click()
                logging.info("Clicked on 'Registration' link using ID.")
            except Exception as e1:
                logging.warning(f"Could not find 'Registration' link by ID. Trying XPath. Error: {e1}")
                try:
                    logging.info("Attempting to find 'Registration' link using XPath.")
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, registration_link_xpath))
                    ).click()
                    logging.info("Clicked on 'Registration' link using XPath.")
                except Exception as e2:
                    logging.warning(f"Could not find 'Registration' link by XPath. Trying link text. Error: {e2}")
                    try:
                        logging.info("Attempting to find 'Registration' link using link text 'Registration'.")
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.LINK_TEXT, 'Registration'))
                        ).click()
                        logging.info("Clicked on 'Registration' link using link text.")
                    except Exception as e3:
                        logging.error(f"Failed to find 'Registration' link with all methods. Error: {e3}")
                        return False

            # Step 2: Attempt to find and click the "Add/Shopping Cart" link
            logging.info("Trying to locate 'Add/Shopping Cart' link with different methods.")
            add_class_link_xpath = '//a[contains(text(), "Add/Shopping Cart") and @data-tracking="myclasses/reg-add"]'
            add_class_link_css = 'a.myasu-tippy-option[title="Add classes"]'

            try:
                logging.info("Attempting to find 'Add/Shopping Cart' link by XPath.")
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, add_class_link_xpath))
                ).click()
                logging.info("Clicked on 'Add/Shopping Cart' link using XPath.")
            except Exception as e1:
                logging.warning(f"Could not find 'Add/Shopping Cart' link by XPath. Trying CSS selector. Error: {e1}")
                try:
                    logging.info("Attempting to find 'Add/Shopping Cart' link using CSS selector.")
                    WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, add_class_link_css))
                    ).click()
                    logging.info("Clicked on 'Add/Shopping Cart' link using CSS selector.")
                except Exception as e2:
                    logging.warning(f"Could not find 'Add/Shopping Cart' link by CSS selector. Trying link text. Error: {e2}")
                    try:
                        logging.info("Attempting to find 'Add/Shopping Cart' link using link text.")
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.LINK_TEXT, 'Add/Shopping Cart'))
                        ).click()
                        logging.info("Clicked on 'Add/Shopping Cart' link using link text.")
                    except Exception as e3:
                        logging.error(f"Failed to find 'Add/Shopping Cart' link with all methods. Error: {e3}")
                        return False

            # Step 3: Click the "Shopping Cart" item in the list
            shopping_cart_xpath = '//a[@id="SCC_LO_FL_WRK_SCC_VIEW_BTN$0"]'
            logging.info("Attempting to locate 'Shopping Cart' link in the list.")
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, shopping_cart_xpath))
            ).click()
            logging.info("Clicked on 'Shopping Cart' link.")

            # Step 4: Click the "2025 Spring - Undergraduate" term link
            term_link_xpath = '//a[@id="SSR_CART_TRM_FL_TERM_DESCR30$0"]'
            logging.info("Attempting to locate '2025 Spring - Undergraduate' term link.")
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, term_link_xpath))
            ).click()
            logging.info("Clicked on '2025 Spring - Undergraduate' term link.")

            # Log current time in milliseconds upon reaching the target page
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            logging.info(f"Reached final page with target button at {current_time}")

            return True

        except Exception as e:
            logging.error(f"Login and navigation failed: {e}")
            return False

    def keep_session_active(self):
        """Keep the session active by performing periodic actions."""
        last_activity_time = time.time()
        
        while True:
            current_time = time.time()
            if current_time - last_activity_time >= KEEP_ALIVE_INTERVAL:
                try:
                    # Perform a small scroll action
                    self.driver.execute_script("window.scrollBy(0, 10);")
                    time.sleep(1)
                    self.driver.execute_script("window.scrollBy(0, -10);")
                    logging.info("Performed a scroll to keep the session active.")
                    
                    # Log the exact time in milliseconds each time the session is kept alive
                    keep_alive_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    logging.info(f"Session keep-alive triggered at {keep_alive_time}")
                    
                    last_activity_time = current_time  # Reset the last activity time

                except Exception as e:
                    logging.error(f"Failed to perform keep-alive action: {e}")
                    break

    def wait_until_target_time(self):
        """Wait until the specified date and time in Mountain Standard Time with millisecond precision."""
        target_datetime = datetime.datetime.strptime(f"{WAIT_DATE} {WAIT_TIME}", "%Y-%m-%d %H:%M:%S")
        target_datetime = pytz.timezone("MST").localize(target_datetime)
        
        logging.info(f"Waiting until {target_datetime} MST to click the target button.")
        
        while datetime.datetime.now(pytz.timezone("MST")) < target_datetime:
            current_time = datetime.datetime.now(pytz.timezone("MST"))
            logging.info(f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S.%f')}")
            time.sleep(0.001)  # Check every millisecond

    def click_target_button(self):
        """Click the specified button on the page once the target time is reached."""
        try:
            logging.info("Attempting to click the target button.")
            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, TARGET_BUTTON_XPATH))
            ).click()
            logging.info('Clicked the target button successfully.')

            # Wait for the confirmation pop-up and click "Yes" if it appears
            try:
                logging.info("Waiting for enrollment confirmation pop-up.")
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located((By.XPATH, CONFIRMATION_POPUP_XPATH))
                )
                logging.info("Enrollment confirmation pop-up detected.")
                
                # Click the "Yes" button
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, CONFIRMATION_YES_BUTTON_XPATH))
                ).click()
                logging.info("Clicked 'Yes' on enrollment confirmation pop-up.")
            except Exception as e:
                logging.warning("Enrollment confirmation pop-up not detected or 'Yes' button not visible.")
                logging.warning(f"Manual intervention may be required. Error: {e}")

        except Exception as e:
            logging.error(f'Failed to click target button: {e}')

def main_enroller():
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Instantiate and use the InvitationSender class
    sender = InvitationSender(USERNAME, PASSWORD)
    if sender.login():
        # Start keep-alive in a separate thread to run concurrently
        import threading
        keep_alive_thread = threading.Thread(target=sender.keep_session_active)
        keep_alive_thread.daemon = True
        keep_alive_thread.start()

        sender.click_target_button()

if __name__ == "__main__":
    main()
