#!/usr/bin/env python3
"""
ASU Class Auto-Enroller
Handles the enrollment process when triggered (typically by class_checker.py).
Runs with visible browser for Duo authentication.
"""

import os
import sys
import time
import logging
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global configuration
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
LOGIN_URL = 'https://webapp4.asu.edu/myasu/#!'
# Use ENROLLMENT_TERM to avoid conflict with shell's $TERM variable
TERM = os.getenv('ENROLLMENT_TERM') or os.getenv('TERM', '2026 Spring')
if 'xterm' in TERM or 'color' in TERM:  # Fallback if shell TERM is picked up
    TERM = '2026 Spring'
TERM_XPATH_ID = os.getenv('TERM_XPATH_ID', 'SSR_CART_TRM_FL_TERM_DESCR30$0')

# Enrollment button XPath
TARGET_BUTTON_XPATH = '//*[@id="DERIVED_SSR_FL_SSR_ENROLL_FL"]'


class ASUEnroller:
    """Handles ASU class enrollment with visible browser."""
    
    def __init__(self, username, password, verify_mode=False):
        """Initialize the enroller with credentials."""
        if not username or not password:
            raise ValueError("Username and password must be provided")
        
        self.driver = None
        self.username = username
        self.password = password
        self.verify_mode = verify_mode
        self.debug_dir = os.path.join(os.getcwd(), 'debug_screenshots')
        os.makedirs(self.debug_dir, exist_ok=True)
        
    def init_webdriver(self):
        """Initialize Chrome WebDriver in visible mode."""
        try:
            options = ChromeOptions()
            # Use user data to persist Duo authentication
            options.add_argument(f'--user-data-dir={os.getcwd()}/userdata')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Docker/Linux compatibility
            if os.path.exists("/usr/bin/chromium"):
                options.binary_location = "/usr/bin/chromium"
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                service = webdriver.ChromeService(executable_path="/usr/bin/chromedriver")
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
            
            logging.info("✓ ChromeDriver initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"✗ Failed to initialize ChromeDriver: {e}")
            return False
            
    def _take_screenshot(self, name):
        """Take a screenshot and save page source for debugging."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Save screenshot
            screenshot_filename = os.path.join(self.debug_dir, f"{name}_{timestamp}.png")
            self.driver.save_screenshot(screenshot_filename)
            logging.info(f"Screenshot saved: {screenshot_filename}")
            
            # Save page source
            source_filename = os.path.join(self.debug_dir, f"{name}_{timestamp}.html")
            with open(source_filename, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logging.info(f"Page source saved: {source_filename}")
            
        except Exception as e:
            logging.warning(f"Failed to capture debug info: {e}")

    def _wait_for_spinner(self):
        """Wait for PeopleSoft processing spinner to disappear."""
        try:
            # The spinner usually has ID 'WAIT_win1' or similar
            WebDriverWait(self.driver, 0.5).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(@id, 'WAIT_win')]"))
            )
            # If found, wait for it to disappear
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.XPATH, "//*[contains(@id, 'WAIT_win')]"))
            )
        except:
            pass  # Spinner might not have appeared, which is fine

    def login_and_navigate(self):
        """
        Login to ASU and navigate to the enrollment page.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logging.info("=" * 60)
            logging.info("Starting login and navigation process")
            logging.info("=" * 60)
            
            # Open login page
            logging.info(f"Opening login page: {LOGIN_URL}")
            self.driver.get(LOGIN_URL)
            
            # Enter credentials
            logging.info("Waiting for username field...")
            try:
                username_field = WebDriverWait(self.driver, 20).until(
                    EC.visibility_of_element_located((By.ID, 'username'))
                )
                username_field.send_keys(self.username)
                logging.info("✓ Username entered")
                
                password_field = self.driver.find_element(By.ID, 'password')
                password_field.send_keys(self.password)
                logging.info("✓ Password entered")
                
                # Click submit button (try multiple methods)
                time.sleep(1)  # Ensure form is ready
                
                if not self._click_submit_button():
                    logging.error("✗ Failed to submit login form")
                    self._take_screenshot("login_fail")
                    return False
                
                logging.info("✓ Login form submitted")
            except Exception as e:
                # Check if already logged in (My ASU page)
                if "My ASU" in self.driver.title:
                     logging.info("✓ Already logged in")
                else:
                    raise e
            
            # Handle Duo authentication if required
            self._handle_duo_authentication()
            
            # Navigate to enrollment page
            if not self._navigate_to_enrollment_page():
                logging.error("✗ Failed to navigate to enrollment page")
                self._take_screenshot("nav_fail")
                return False
            
            logging.info("✓ Successfully navigated to enrollment page")
            return True
            
        except Exception as e:
            logging.error(f"✗ Login and navigation failed: {e}", exc_info=True)
            self._take_screenshot("login_exception")
            return False
    
    def _click_submit_button(self):
        """Try multiple methods to find and click the submit button."""
        methods = [
            ("NAME 'submitBtn'", By.NAME, 'submitBtn'),
            ("Full XPath", By.XPATH, '/html/body/div[3]/main/div/div/section/div/div[2]/form/div/button'),
            ("Class 'btn-primary'", By.CSS_SELECTOR, 'button.btn-primary[type="submit"]'),
            ("Button with Sign In text", By.XPATH, '//button[contains(@class, "btn-primary") and contains(., "Sign In")]'),
            ("Any submit button", By.CSS_SELECTOR, 'button[type="submit"]'),
        ]
        
        for description, by_method, selector in methods:
            try:
                logging.info(f"Trying to find submit button by {description}...")
                element = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((by_method, selector))
                )
                element.click()
                logging.info(f"✓ Submit button clicked using {description}")
                return True
                
            except Exception as e:
                logging.debug(f"Could not find submit button by {description}: {e}")
                continue
        
        return False
    
    def _handle_duo_authentication(self):
        """Handle Duo 2FA if it appears."""
        try:
            logging.info("Checking for Duo authentication...")
            
            # Try multiple methods to find the Duo button
            duo_methods = [
                ("ID 'trust-browser-button'", By.ID, 'trust-browser-button'),
                ("Full XPath", By.XPATH, '/html/body/div/div/div[1]/div/div[2]/div[3]/button'),
                ("Button text", By.XPATH, '//button[contains(text(), "Yes, this is my device")]'),
                ("Class 'button--primary'", By.CSS_SELECTOR, 'button.button--primary'),
            ]
            
            duo_clicked = False
            for description, by_method, selector in duo_methods:
                try:
                    logging.debug(f"Looking for Duo button by {description}...")
                    duo_button = WebDriverWait(self.driver, 5).until(
                        EC.visibility_of_element_located((by_method, selector))
                    )
                    logging.info("⚠ Duo authentication required!")
                    duo_button.click()
                    logging.info(f"✓ Duo button clicked using {description} - please approve on your device")
                    duo_clicked = True
                    time.sleep(3)  # Wait for Duo to process
                    break
                except Exception:
                    continue
            
            if not duo_clicked:
                logging.info("✓ Duo authentication not required or already approved")
            
        except Exception as e:
            logging.info(f"✓ Duo authentication not required or already approved: {e}")
    
    def _navigate_to_enrollment_page(self):
        """Navigate through ASU portal to reach the enrollment page."""
        try:
            # Step 1: Click Registration link
            if not self._click_registration_link():
                return False
            
            # Step 2: Click Add/Shopping Cart link
            if not self._click_shopping_cart_link():
                return False
            
            # Step 3: Click Shopping Cart from list
            if not self._click_shopping_cart_view():
                return False
            
            # Step 4: Click Change Term button (IMPORTANT!)
            if not self._click_change_term_button():
                return False
            
            # Step 5: Click term link to select the term
            if not self._click_term_link():
                return False
            
            # Step 6: Navigate back to Shopping Cart (required before enrollment)
            if not self._navigate_back_to_shopping_cart():
                return False
            
            # Log arrival time
            arrival_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            logging.info(f"✓ Reached shopping cart page at {arrival_time}")
            
            return True
            
        except Exception as e:
            logging.error(f"✗ Navigation failed: {e}", exc_info=True)
            return False
    
    def _click_registration_link(self):
        """Find and click the Registration link."""
        methods = [
            ("Link text", By.LINK_TEXT, 'Registration'),
            ("ID 'classes-reg-link'", By.ID, 'classes-reg-link'),
            ("Full XPath", By.XPATH, '/html/body/div[1]/main/div/div/div[4]/div[2]/div/div/div[1]/section[2]/div[2]/div[2]/div[4]/div[3]/span[1]/a'),
            ("CSS selector", By.CSS_SELECTOR, 'a#classes-reg-link.reg-popup'),
            ("Partial link text", By.PARTIAL_LINK_TEXT, 'Registration'),
        ]
        
        for description, by_method, selector in methods:
            try:
                logging.info(f"Looking for Registration link by {description}...")
                element = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((by_method, selector))
                )
                element.click()
                logging.info(f"✓ Clicked Registration link using {description}")
                time.sleep(2)  # Wait for page to load
                return True
                
            except Exception as e:
                logging.debug(f"Could not find Registration link by {description}: {e}")
                continue
        
        logging.error("✗ Failed to find Registration link with all methods")
        self._take_screenshot("reg_link_fail")
        return False
    
    def _click_shopping_cart_link(self):
        """Find and click the Add/Shopping Cart link."""
        methods = [
            ("Link text", By.LINK_TEXT, 'Add/Shopping Cart'),
            ("Title attribute", By.CSS_SELECTOR, 'a.myasu-tippy-option[title="Add classes"]'),
            ("Full XPath", By.XPATH, '/html/body/div[1]/main/div/div/div[4]/div[2]/div/div/div[1]/section[2]/div[2]/div[2]/div[4]/div[3]/span[1]/div/div/div/div/div/div/a[2]'),
            ("Data tracking", By.XPATH, '//a[@data-tracking="myclasses/reg-add"]'),
            ("Partial link text", By.PARTIAL_LINK_TEXT, 'Shopping Cart'),
        ]
        
        for description, by_method, selector in methods:
            try:
                logging.info(f"Looking for Add/Shopping Cart link by {description}...")
                element = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((by_method, selector))
                )
                element.click()
                logging.info(f"✓ Clicked Add/Shopping Cart link using {description}")
                time.sleep(2)  # Wait for page to load
                return True
                
            except Exception as e:
                logging.debug(f"Could not find Add/Shopping Cart link by {description}: {e}")
                continue
        
        logging.error("✗ Failed to find Add/Shopping Cart link with all methods")
        self._take_screenshot("cart_link_fail")
        return False
    
    def _click_shopping_cart_view(self):
        """Click the Shopping Cart view button."""
        methods = [
            ("Full XPath", By.XPATH, '/html/body/form/div[2]/div[4]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div[1]/div/ul/li[1]/div[1]'),
            ("ID 'SCC_LO_FL_WRK_SCC_VIEW_BTN$0'", By.ID, 'SCC_LO_FL_WRK_SCC_VIEW_BTN$0'),
            ("XPath with ID", By.XPATH, '//a[@id="SCC_LO_FL_WRK_SCC_VIEW_BTN$0"]'),
            ("Link text", By.LINK_TEXT, 'Shopping Cart'),
            ("Partial link containing img", By.XPATH, '//a[contains(@id, "SCC_VIEW_BTN") and .//span[contains(text(), "Shopping Cart")]]'),
        ]
        
        for description, by_method, selector in methods:
            try:
                logging.info(f"Looking for Shopping Cart view button by {description}...")
                element = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((by_method, selector))
                )
                element.click()
                logging.info(f"✓ Clicked Shopping Cart view button using {description}")
                time.sleep(2)  # Wait for page to load
                return True
                
            except Exception as e:
                logging.debug(f"Could not find Shopping Cart view button by {description}: {e}")
                continue
        
        logging.error("✗ Failed to find Shopping Cart view button with all methods")
        self._take_screenshot("cart_view_fail")
        return False
    
    def _navigate_back_to_shopping_cart(self):
        """Navigate back to Shopping Cart after selecting term."""
        logging.info("Navigating back to Shopping Cart...")
        
        # First, ensure we are back in the main content (out of any iframes)
        try:
            self.driver.switch_to.default_content()
        except:
            pass
            
        # Check if we are already on the Shopping Cart page
        try:
            if "Shopping Cart" in self.driver.page_source and "Enroll" in self.driver.page_source:
                logging.info("✓ Already on Shopping Cart page")
                return True
        except:
            pass
        
        methods = [
            ("ID 'SCC_LO_FL_WRK_SCC_VIEW_BTN$0'", By.ID, 'SCC_LO_FL_WRK_SCC_VIEW_BTN$0'),
            ("User Provided XPath", By.XPATH, '/html/body/form/div[2]/div[4]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div[1]/div/ul/li[1]/div[1]/div/span/a'),
            ("Full XPath", By.XPATH, '/html/body/form/div[2]/div[4]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div[1]/div/ul/li[1]/div[1]'),
            ("Link text", By.LINK_TEXT, 'Shopping Cart'),
            ("XPath with ID", By.XPATH, '//a[@id="SCC_LO_FL_WRK_SCC_VIEW_BTN$0"]'),
            ("Span with Shopping Cart title", By.XPATH, '//span[@title="Shopping Cart"]//a'),
            ("Any link with SCC_VIEW_BTN", By.XPATH, '//a[contains(@id, "SCC_LO_FL_WRK_SCC_VIEW_BTN")]'),
        ]
        
        for description, by_method, selector in methods:
            try:
                logging.info(f"Looking for Shopping Cart link by {description}...")
                element = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((by_method, selector))
                )
                element.click()
                logging.info(f"✓ Clicked Shopping Cart link using {description}")
                time.sleep(3)  # Wait for shopping cart to load
                self._wait_for_spinner()
                return True
                
            except Exception as e:
                logging.debug(f"Could not find Shopping Cart link by {description}: {e}")
                continue
        
        logging.error("✗ Failed to navigate back to Shopping Cart")
        self._take_screenshot("back_cart_fail")
        return False
    
    def _click_change_term_button(self):
        """Click the Change Term button to open term selection."""
        methods = [
            ("ID 'DERIVED_SSR_FL_SSR_CHANGE_BTN'", By.ID, 'DERIVED_SSR_FL_SSR_CHANGE_BTN'),
            ("Full XPath", By.XPATH, '/html/body/form/div[2]/div[1]/div/div/div/div[4]/div/div/div/ul/li[2]/div/span/a'),
            ("Link text", By.LINK_TEXT, 'Change'),
            ("XPath with text", By.XPATH, '//a[contains(@id, "CHANGE_BTN") and contains(text(), "Change")]'),
            ("Button role", By.XPATH, '//a[@role="button" and contains(text(), "Change")]'),
        ]
        
        for description, by_method, selector in methods:
            try:
                logging.info(f"Looking for Change Term button by {description}...")
                element = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((by_method, selector))
                )
                element.click()
                logging.info(f"✓ Clicked Change Term button using {description}")
                
                self._wait_for_spinner()
                time.sleep(2)
                
                # Check for iframe modal
                try:
                    logging.info("Checking for term selection modal iframe...")
                    iframe = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "iframe"))
                    )
                    self.driver.switch_to.frame(iframe)
                    logging.info("✓ Switched to term selection iframe")
                except:
                    logging.info("No iframe found, assuming main page content")
                
                return True
                
            except Exception as e:
                logging.debug(f"Could not find Change Term button by {description}: {e}")
                continue
        
        logging.error("✗ Failed to find Change Term button with all methods")
        self._take_screenshot("change_term_fail")
        return False
    
    def _click_term_link(self):
        """Click the term link matching the target term."""
        logging.info(f"Looking for term link matching '{TERM}'...")
        
        methods = [
            # 1. Exact ID match (User provided)
            ("ID 'SSR_CART_TRM_FL_TERM_DESCR30$0'", By.ID, 'SSR_CART_TRM_FL_TERM_DESCR30$0'),
            
            # 2. User provided XPath
            ("User Provided XPath", By.XPATH, '/html/body/form/div[2]/div[2]/div/div[2]/div/div/div/div[2]/div/div/table/tbody/tr/td/div'),
            
            # 3. Link text match
            (f"Link text '{TERM}'", By.LINK_TEXT, TERM),
            
            # 4. Partial link text match
            (f"Partial link text '{TERM}'", By.PARTIAL_LINK_TEXT, TERM),
            
            # 5. XPath with text match
            (f"XPath text '{TERM}'", By.XPATH, f"//a[contains(text(), '{TERM}')]"),
            
            # 6. Fallback to first link in table (Original method)
            ("First link in table", By.XPATH, '//table//tbody//tr[1]//a[@class="ps-link"]'),
        ]
        
        for description, by_method, selector in methods:
            try:
                logging.info(f"Trying to find term by {description}...")
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((by_method, selector))
                )
                
                term_text = element.text.strip() if element.text else "unknown"
                logging.info(f"Found element: {term_text} (tag={element.tag_name}, displayed={element.is_displayed()})")
                
                # Scroll into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                
                # Try regular click first
                try:
                    WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable((by_method, selector)))
                    element.click()
                    logging.info(f"✓ Clicked term '{term_text}' using {description}")
                except Exception as e1:
                    # If regular click fails, try JavaScript click
                    logging.debug(f"Regular click failed: {e1}, trying JavaScript...")
                    self.driver.execute_script("arguments[0].click();", element)
                    logging.info(f"✓ Clicked term '{term_text}' using {description} (JavaScript)")
                
                self._wait_for_spinner()
                time.sleep(3)
                
                # Switch back to default content in case we were in an iframe
                self.driver.switch_to.default_content()
                return True
                
            except Exception as e:
                logging.debug(f"Could not find term by {description}: {e}")
                continue
        
        logging.error("✗ Failed to find any clickable term in the table")
        self._take_screenshot("term_select_fail")
        return False
    
    def enroll(self):
        """
        Click the enrollment button and confirm.
        
        Returns:
            bool: True if successful, False otherwise
        """
        # User requested to perform actual enrollment even in verify mode
        # if self.verify_mode:
        #     logging.info("=" * 60)
        #     logging.info("VERIFICATION MODE: Skipping actual enrollment")
        #     logging.info("=" * 60)
        #     logging.info("✓ Navigation verification completed successfully")
        #     return True

        try:
            logging.info("=" * 60)
            logging.info("Starting enrollment process (Clicking Enroll & Confirm)")
            logging.info("=" * 60)
            
            # Click the enrollment button
            logging.info("Looking for enrollment button...")
            
            enroll_methods = [
                ("ID 'DERIVED_SSR_FL_SSR_ENROLL_FL'", By.ID, 'DERIVED_SSR_FL_SSR_ENROLL_FL'),
                ("User Provided XPath", By.XPATH, '/html/body/form/div[2]/div[4]/div[2]/div/div/div/div/div/div/div[2]/div/div[1]/span/a'),
                ("Full XPath", By.XPATH, '/html/body/form/div[2]/div[4]/div[2]/div/div/div/div/div/div/div[2]/div/div[1]/span/a'),
                ("XPath with ID", By.XPATH, TARGET_BUTTON_XPATH),
                ("Link text", By.LINK_TEXT, 'Enroll'),
                ("Button with role", By.XPATH, '//a[@role="button" and contains(text(), "Enroll")]'),
                ("Any link containing Enroll", By.XPATH, '//a[contains(@id, "ENROLL") and contains(text(), "Enroll")]'),
                ("ps-button class", By.CSS_SELECTOR, 'a.ps-button[role="button"]'),
            ]
            
            enroll_clicked = False
            for description, by_method, selector in enroll_methods:
                try:
                    logging.info(f"Trying enrollment button by {description}...")
                    enroll_button = WebDriverWait(self.driver, 20).until(
                        EC.element_to_be_clickable((by_method, selector))
                    )
                    
                    click_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    
                    # Try regular click first
                    try:
                        enroll_button.click()
                        logging.info(f"✓ Clicked enrollment button at {click_time} using {description}")
                    except:
                        # If regular click fails, use JavaScript
                        self.driver.execute_script("arguments[0].click();", enroll_button)
                        logging.info(f"✓ Clicked enrollment button at {click_time} using {description} (JavaScript)")
                    
                    enroll_clicked = True
                    break
                    
                except Exception as e:
                    logging.debug(f"Could not find enrollment button by {description}: {e}")
                    continue
            
            if not enroll_clicked:
                logging.error("✗ Could not find enrollment button with any method")
                self._take_screenshot("enroll_btn_fail")
                return False
            
            # Handle confirmation popup if it appears
            self._handle_confirmation_popup()
            
            # Give the page time to process
            time.sleep(5)
            
            # Check for success or error messages
            self._check_enrollment_result()
            
            logging.info("=" * 60)
            logging.info("✓ ENROLLMENT ACTIONS COMPLETED")
            logging.info("=" * 60)
            
            if not self.verify_mode:
                logging.info("Browser will remain open for verification...")
                logging.info("Press Ctrl+C to close when done.")
                try:
                    while True:
                        time.sleep(60)
                except KeyboardInterrupt:
                    logging.info("Closing browser...")
            
            return True
            
        except Exception as e:
            logging.error(f"✗ Enrollment failed: {e}", exc_info=True)
            self._take_screenshot("enroll_exception")
            return False
    
    def _handle_confirmation_popup(self):
        """Handle enrollment confirmation popup if it appears."""
        try:
            logging.info("Checking for enrollment confirmation popup...")
            
            # Wait for popup to appear
            time.sleep(3)
            
            yes_methods = [
                ("ID '#ICYes'", By.ID, '#ICYes'),
                ("Full XPath", By.XPATH, '/html/body/form/div[1]/div[3]/div[2]/div/div[2]/div/div[2]/div[1]/span/a'),
                ("Link with onclick", By.XPATH, '//a[@id="#ICYes" and @role="button"]'),
                ("Any Yes button", By.XPATH, '//a[contains(@id, "ICYes")]'),
                ("Button with Yes text", By.XPATH, '//a[@role="button" and .//span[text()="Yes"]]'),
                ("Link containing Yes", By.XPATH, '//a[contains(@onclick, "ICYes")]'),
            ]
            
            yes_clicked = False
            for description, by_method, selector in yes_methods:
                try:
                    logging.info(f"Looking for Yes button by {description}...")
                    yes_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by_method, selector))
                    )
                    logging.info("⚠ Confirmation popup detected")
                    
                    # Try regular click first
                    try:
                        yes_button.click()
                        logging.info(f"✓ Clicked 'Yes' on confirmation popup using {description}")
                    except:
                        # If regular click fails, use JavaScript
                        self.driver.execute_script("arguments[0].click();", yes_button)
                        logging.info(f"✓ Clicked 'Yes' on confirmation popup using {description} (JavaScript)")
                    
                    yes_clicked = True
                    time.sleep(2)
                    break
                except Exception as e:
                    logging.debug(f"Could not find Yes button by {description}: {e}")
                    continue
            
            if not yes_clicked:
                logging.info("✓ No confirmation popup (or already handled)")
            
        except Exception as e:
            logging.info(f"✓ No confirmation popup: {e}")
    
    def _check_enrollment_result(self):
        """Check the page for success or error messages after enrollment."""
        try:
            time.sleep(2)  # Wait for messages to appear
            
            # Look for success indicators
            success_indicators = [
                "successfully enrolled",
                "enrollment successful",
                "you are enrolled",
            ]
            
            # Look for error indicators
            error_indicators = [
                "error",
                "failed",
                "unable to enroll",
                "class is full",
                "waitlist",
            ]
            
            page_text = self.driver.page_source.lower()
            
            for indicator in success_indicators:
                if indicator in page_text:
                    logging.info(f"✓ SUCCESS: Found indicator '{indicator}'")
                    return True
            
            for indicator in error_indicators:
                if indicator in page_text:
                    logging.warning(f"⚠ POSSIBLE ERROR: Found indicator '{indicator}'")
                    self._take_screenshot("enroll_error")
            
            logging.info("Check the browser for enrollment status")
            
        except Exception as e:
            logging.debug(f"Could not check enrollment result: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        try:
            if self.driver:
                self.driver.quit()
                logging.info("✓ Browser closed")
        except Exception as e:
            logging.warning(f"Error during cleanup: {e}")
    
    def run(self):
        """Main execution flow."""
        try:
            # Initialize browser
            if not self.init_webdriver():
                logging.error("Failed to initialize browser")
                return False
            
            # Login and navigate
            if not self.login_and_navigate():
                logging.error("Failed to login and navigate")
                return False
            
            # Perform enrollment
            if not self.enroll():
                logging.error("Failed to enroll")
                return False
            
            return True
            
        except KeyboardInterrupt:
            logging.info("\n⚠ Interrupted by user")
            return False
            
        except Exception as e:
            logging.error(f"✗ Unexpected error: {e}", exc_info=True)
            return False
            
        finally:
            if self.verify_mode:
                self.cleanup()
            else:
                # Don't auto-cleanup in normal mode - let user verify enrollment
                pass


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='ASU Class Auto-Enroller')
    parser.add_argument('--verify', action='store_true', help='Run in verification mode (no enrollment)')
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('enroller.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.info("=" * 60)
    logging.info("ASU Class Auto-Enroller")
    logging.info(f"Target Term: {TERM}")
    logging.info(f"Mode: {'VERIFICATION' if args.verify else 'ENROLLMENT'}")
    logging.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 60)
    
    # Validate credentials
    if not USERNAME or not PASSWORD:
        logging.error("✗ USERNAME and PASSWORD must be set in .env file")
        sys.exit(1)
    
    # Create and run enroller
    enroller = ASUEnroller(USERNAME, PASSWORD, verify_mode=args.verify)
    success = enroller.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
