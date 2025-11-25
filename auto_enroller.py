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

# Confirmation pop-up XPaths
CONFIRMATION_POPUP_XPATH = '//*[@id="ptModTable_0"]'
CONFIRMATION_YES_BUTTON_XPATH = '//*[@id="#ICYes"]'


class ASUEnroller:
    """Handles ASU class enrollment with visible browser."""
    
    def __init__(self, username, password):
        """Initialize the enroller with credentials."""
        if not username or not password:
            raise ValueError("Username and password must be provided")
        
        self.driver = None
        self.username = username
        self.password = password
        
    def init_webdriver(self):
        """Initialize Chrome WebDriver in visible mode."""
        try:
            options = ChromeOptions()
            # Use user data to persist Duo authentication
            options.add_argument(f'--user-data-dir={os.getcwd()}/userdata')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
            
            logging.info("✓ ChromeDriver initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"✗ Failed to initialize ChromeDriver: {e}")
            return False
    
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
                return False
            
            logging.info("✓ Login form submitted")
            
            # Handle Duo authentication if required
            self._handle_duo_authentication()
            
            # Navigate to enrollment page
            if not self._navigate_to_enrollment_page():
                logging.error("✗ Failed to navigate to enrollment page")
                return False
            
            logging.info("✓ Successfully navigated to enrollment page")
            return True
            
        except Exception as e:
            logging.error(f"✗ Login and navigation failed: {e}", exc_info=True)
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
            
            # Log arrival time
            arrival_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            logging.info(f"✓ Reached enrollment page at {arrival_time}")
            
            return True
            
        except Exception as e:
            logging.error(f"✗ Navigation failed: {e}", exc_info=True)
            return False
    
    def _click_registration_link(self):
        """Find and click the Registration link."""
        methods = [
            ("ID 'classes-reg-link'", By.ID, 'classes-reg-link'),
            ("Full XPath", By.XPATH, '/html/body/div[1]/main/div/div/div[4]/div[2]/div/div/div[1]/section[2]/div[2]/div[2]/div[4]/div[3]/span[1]/a'),
            ("CSS selector", By.CSS_SELECTOR, 'a#classes-reg-link.reg-popup'),
            ("Link text", By.LINK_TEXT, 'Registration'),
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
        return False
    
    def _click_shopping_cart_link(self):
        """Find and click the Add/Shopping Cart link."""
        methods = [
            ("Title attribute", By.CSS_SELECTOR, 'a.myasu-tippy-option[title="Add classes"]'),
            ("Full XPath", By.XPATH, '/html/body/div[1]/main/div/div/div[4]/div[2]/div/div/div[1]/section[2]/div[2]/div[2]/div[4]/div[3]/span[1]/div/div/div/div/div/div/a[2]'),
            ("Data tracking", By.XPATH, '//a[@data-tracking="myclasses/reg-add"]'),
            ("Link text", By.LINK_TEXT, 'Add/Shopping Cart'),
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
        return False
    
    def _click_shopping_cart_view(self):
        """Click the Shopping Cart view button."""
        methods = [
            ("ID 'SCC_LO_FL_WRK_SCC_VIEW_BTN$0'", By.ID, 'SCC_LO_FL_WRK_SCC_VIEW_BTN$0'),
            ("Full XPath", By.XPATH, '/html/body/form/div[2]/div[4]/div[1]/div/div[2]/div[1]/div/div/div/div/div/div/div[1]/div/ul/li[1]/div[1]'),
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
                time.sleep(2)  # Wait for term selection to appear
                return True
                
            except Exception as e:
                logging.debug(f"Could not find Change Term button by {description}: {e}")
                continue
        
        logging.error("✗ Failed to find Change Term button with all methods")
        return False
    
    def _click_term_link(self):
        """Click the term link to select the specified term."""
        methods = [
            ("ID with term", By.ID, TERM_XPATH_ID),
            ("Link text exact", By.LINK_TEXT, TERM),
            ("XPath with ID", By.XPATH, f'//a[@id="{TERM_XPATH_ID}"]'),
            ("XPath with text", By.XPATH, f'//a[contains(text(), "{TERM}")]'),
            ("Table row click", By.XPATH, f'//tr[.//a[contains(text(), "{TERM}")]]'),
            ("Any link with 2026 Spring", By.XPATH, '//a[contains(., "2026 Spring") and contains(@class, "ps-link")]'),
        ]
        
        for description, by_method, selector in methods:
            try:
                logging.info(f"Looking for '{TERM}' term link by {description}...")
                element = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((by_method, selector))
                )
                element.click()
                logging.info(f"✓ Clicked '{TERM}' term link using {description}")
                time.sleep(3)  # Wait for enrollment page to load
                return True
                
            except Exception as e:
                logging.debug(f"Could not find term link by {description}: {e}")
                continue
        
        logging.error(f"✗ Failed to find '{TERM}' term link with all methods")
        return False
    
    def enroll(self):
        """
        Click the enrollment button and confirm.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logging.info("=" * 60)
            logging.info("Starting enrollment process")
            logging.info("=" * 60)
            
            # Click the enrollment button
            logging.info("Looking for enrollment button...")
            
            enroll_methods = [
                ("ID 'DERIVED_SSR_FL_SSR_ENROLL_FL'", By.ID, 'DERIVED_SSR_FL_SSR_ENROLL_FL'),
                ("XPath with ID", By.XPATH, TARGET_BUTTON_XPATH),
                ("Link text", By.LINK_TEXT, 'Enroll'),
                ("Button with role", By.XPATH, '//a[@role="button" and contains(text(), "Enroll")]'),
                ("Any link containing Enroll", By.XPATH, '//a[contains(@id, "ENROLL") and contains(text(), "Enroll")]'),
            ]
            
            enroll_clicked = False
            for description, by_method, selector in enroll_methods:
                try:
                    logging.info(f"Trying enrollment button by {description}...")
                    enroll_button = WebDriverWait(self.driver, 20).until(
                        EC.element_to_be_clickable((by_method, selector))
                    )
                    
                    click_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    enroll_button.click()
                    logging.info(f"✓ Clicked enrollment button at {click_time} using {description}")
                    enroll_clicked = True
                    break
                    
                except Exception as e:
                    logging.debug(f"Could not find enrollment button by {description}: {e}")
                    continue
            
            if not enroll_clicked:
                logging.error("✗ Could not find enrollment button with any method")
                return False
            
            # Handle confirmation popup if it appears
            self._handle_confirmation_popup()
            
            # Give the page time to process
            time.sleep(3)
            
            # Check for success or error messages
            self._check_enrollment_result()
            
            logging.info("=" * 60)
            logging.info("✓ ENROLLMENT PROCESS COMPLETED!")
            logging.info("=" * 60)
            logging.info("Please verify enrollment status on the page.")
            
            # Keep browser open for verification
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
            return False
    
    def _handle_confirmation_popup(self):
        """Handle enrollment confirmation popup if it appears."""
        try:
            logging.info("Checking for enrollment confirmation popup...")
            
            # Wait for popup to appear
            time.sleep(2)
            
            yes_methods = [
                ("ID '#ICYes'", By.ID, '#ICYes'),
                ("Full XPath", By.XPATH, '/html/body/form/div[1]/div[3]/div[2]/div/div[2]/div/div[2]/div[1]/span/a'),
                ("Link with onclick", By.XPATH, '//a[@id="#ICYes" and @role="button"]'),
                ("Any Yes button", By.XPATH, '//a[contains(@id, "ICYes")]'),
                ("Button with Yes text", By.XPATH, '//a[@role="button" and .//span[text()="Yes"]]'),
            ]
            
            yes_clicked = False
            for description, by_method, selector in yes_methods:
                try:
                    logging.debug(f"Looking for Yes button by {description}...")
                    yes_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by_method, selector))
                    )
                    logging.info("⚠ Confirmation popup detected")
                    yes_button.click()
                    logging.info(f"✓ Clicked 'Yes' on confirmation popup using {description}")
                    yes_clicked = True
                    time.sleep(2)
                    break
                except Exception:
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
            # Don't auto-cleanup - let user verify enrollment
            pass


def main():
    """Main entry point."""
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
    logging.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("=" * 60)
    
    # Validate credentials
    if not USERNAME or not PASSWORD:
        logging.error("✗ USERNAME and PASSWORD must be set in .env file")
        sys.exit(1)
    
    # Create and run enroller
    enroller = ASUEnroller(USERNAME, PASSWORD)
    success = enroller.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
