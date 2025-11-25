#!/usr/bin/env python3
"""
Class Availability Checker
Runs in headless mode to monitor ASU class availability.
When seats become available, triggers the enrollment script.
"""

import os
import sys
import time
import logging
import subprocess
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
CLASS_NUMBER = os.getenv('CLASS_NUMBER', '22513')
TERM_CODE = os.getenv('TERM_CODE', '2261')  # 2261 = Spring 2026
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '2'))  # seconds
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
ENROLLER_SCRIPT = os.path.join(os.path.dirname(__file__), 'auto_enroller.py')

# Set ENROLLMENT_TERM in environment for enroller script
os.environ['ENROLLMENT_TERM'] = os.getenv('ENROLLMENT_TERM', '2026 Spring')


class ClassAvailabilityChecker:
    """Monitors class availability and triggers enrollment when seats open."""
    
    def __init__(self):
        self.driver = None
        self.retry_count = 0
        self.last_status = None
        
    def init_webdriver(self):
        """Initialize Chrome WebDriver in headless mode."""
        try:
            options = ChromeOptions()
            # Headless mode configuration
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=options)
            logging.info("✓ Headless ChromeDriver initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"✗ Failed to initialize ChromeDriver: {e}")
            return False
    
    def check_availability(self):
        """
        Check if the class has available seats.
        
        Returns:
            tuple: (available: bool, status_text: str, error: str or None)
        """
        try:
            catalog_url = (
                f"https://catalog.apps.asu.edu/catalog/classes/classlist?"
                f"campusOrOnlineSelection=A&honors=F&keywords={CLASS_NUMBER}"
                f"&promod=F&searchType=all&term={TERM_CODE}"
            )
            
            logging.debug(f"Navigating to catalog page for class {CLASS_NUMBER}")
            self.driver.get(catalog_url)
            
            # Wait for the class status element to load
            try:
                class_status_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='class-results-cell seats']/div[@class='text-nowrap']")
                    )
                )
                
                availability_text = class_status_element.text.strip()
                
                if not availability_text:
                    return False, "Unknown", "Could not read availability text"
                
                # Check if seats are available (not "0 of X")
                is_available = "0 of" not in availability_text
                
                return is_available, availability_text, None
                
            except Exception as e:
                logging.warning(f"Could not locate class status element: {e}")
                return False, "Not found", str(e)
                
        except Exception as e:
            logging.error(f"Error checking class availability: {e}")
            return False, "Error", str(e)
    
    def trigger_enrollment(self):
        """
        Trigger the enrollment script in normal (non-headless) mode.
        
        Returns:
            bool: True if successfully triggered, False otherwise
        """
        try:
            logging.info("=" * 60)
            logging.info("🎉 SEATS AVAILABLE! Triggering enrollment script...")
            logging.info("=" * 60)
            
            # Close the headless browser before launching the visible one
            if self.driver:
                try:
                    self.driver.quit()
                    logging.info("✓ Closed headless browser")
                except Exception as e:
                    logging.warning(f"Could not close headless browser: {e}")
            
            # Launch the enrollment script in a new process
            if not os.path.exists(ENROLLER_SCRIPT):
                logging.error(f"✗ Enrollment script not found: {ENROLLER_SCRIPT}")
                return False
            
            logging.info(f"Launching: python3 {ENROLLER_SCRIPT}")
            
            # Run the enroller script
            process = subprocess.Popen(
                ['python3', ENROLLER_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logging.info(f"✓ Enrollment script launched (PID: {process.pid})")
            
            # Wait for the process to complete and capture output
            stdout, stderr = process.communicate(timeout=300)  # 5 minute timeout
            
            if process.returncode == 0:
                logging.info("✓ Enrollment script completed successfully")
                if stdout:
                    logging.info(f"Enrollment output:\n{stdout}")
                return True
            else:
                logging.error(f"✗ Enrollment script failed with exit code {process.returncode}")
                if stderr:
                    logging.error(f"Error output:\n{stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logging.error("✗ Enrollment script timed out after 5 minutes")
            process.kill()
            return False
            
        except Exception as e:
            logging.error(f"✗ Failed to trigger enrollment: {e}")
            return False
    
    def run(self):
        """Main monitoring loop."""
        logging.info("=" * 60)
        logging.info("ASU Class Availability Checker")
        logging.info("=" * 60)
        logging.info(f"Class Number: {CLASS_NUMBER}")
        logging.info(f"Term Code: {TERM_CODE}")
        logging.info(f"Check Interval: {CHECK_INTERVAL} seconds")
        logging.info(f"Starting at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info("=" * 60)
        
        # Initialize browser
        if not self.init_webdriver():
            logging.error("Failed to initialize browser. Exiting.")
            return False
        
        try:
            while True:
                try:
                    is_available, status_text, error = self.check_availability()
                    
                    # Only log status changes to avoid spam
                    if status_text != self.last_status:
                        logging.info(f"Class {CLASS_NUMBER} status: {status_text}")
                        self.last_status = status_text
                    else:
                        logging.debug(f"Status unchanged: {status_text}")
                    
                    if is_available:
                        # Seats are available! Trigger enrollment
                        if self.trigger_enrollment():
                            logging.info("✓ Enrollment triggered successfully. Exiting checker.")
                            return True
                        else:
                            logging.error("✗ Enrollment trigger failed. Will retry checking...")
                            # Reinitialize browser and continue checking
                            self.driver.quit()
                            if not self.init_webdriver():
                                logging.error("Could not reinitialize browser. Exiting.")
                                return False
                    
                    if error:
                        self.retry_count += 1
                        if self.retry_count >= MAX_RETRIES:
                            logging.error(f"Max retries ({MAX_RETRIES}) reached. Restarting browser...")
                            self.driver.quit()
                            if not self.init_webdriver():
                                logging.error("Could not reinitialize browser. Exiting.")
                                return False
                            self.retry_count = 0
                    else:
                        self.retry_count = 0
                    
                    # Wait before next check
                    time.sleep(CHECK_INTERVAL)
                    
                except KeyboardInterrupt:
                    logging.info("\n⚠ Interrupted by user. Shutting down...")
                    raise
                    
                except Exception as e:
                    logging.error(f"Error in monitoring loop: {e}")
                    self.retry_count += 1
                    
                    if self.retry_count >= MAX_RETRIES:
                        logging.error("Too many errors. Attempting to restart browser...")
                        try:
                            if self.driver:
                                self.driver.quit()
                            if not self.init_webdriver():
                                logging.error("Could not reinitialize browser. Exiting.")
                                return False
                            self.retry_count = 0
                        except Exception as e2:
                            logging.error(f"Failed to restart browser: {e2}")
                            return False
                    
                    time.sleep(CHECK_INTERVAL)
                    
        except KeyboardInterrupt:
            logging.info("Shutting down gracefully...")
            return True
            
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                    logging.info("✓ Browser closed")
                except Exception as e:
                    logging.warning(f"Could not close browser: {e}")


def main():
    """Main entry point."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('checker.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create and run checker
    checker = ClassAvailabilityChecker()
    success = checker.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

