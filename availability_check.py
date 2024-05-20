import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

# Initialize WebDriver
service = Service('C:\\Users\\sriuj\\classauto\\chromedriver-win64\\chromedriver-win64\\chromedriver.exe')
driver = webdriver.Chrome(service=service)
driver.get('https://webapp4.asu.edu/myasu/')

# Load cookies
with open('cookies.pkl', 'rb') as file:
    cookies = pickle.load(file)

current_domain = driver.current_url.split('/')[2]  # Extract domain from current URL

# Add cookies to the current domain
for cookie in cookies:
    cookie['domain'] = current_domain  # Update the domain of the cookie
    try:
        driver.add_cookie(cookie)
    except Exception as e:
        print(f"Error adding cookie: {e}")
        
def swap_class():
    try:
        driver.get('https://cs.oasis.asu.edu/psc/asucsprd/EMPLOYEE/PSFT_ASUCSPRD/c/SSR_STUDENT_FL.SSR_SWAP_CLASS_FL.GBL?Page=SSR_SWAP_TERM_FL')
        
        
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Refresh the page to use the loaded cookies
driver.refresh()

swap_class()

# Navigate to the class enrollment page
driver.get('https://catalog.apps.asu.edu/catalog/classes/classlist?campusOrOnlineSelection=C&catalogNbr=355&honors=F&keywords=83573&promod=F&searchType=all&subject=CSE&term=2247')

# Allow some time for the page to load
time.sleep(5)

# Check if the class is open or not based on the number of seats available
def check_class_availability():
    try:
        seats_text = driver.find_element(By.CSS_SELECTOR, 'div.class-results-cell.seats > div.text-nowrap').text
        open_seats = int(seats_text.split(' ')[0])
        
        if open_seats > 0:
            swap_class()
        else:
            #give a 5 second delay before checking again
            time.sleep(5)
            print("The class is not open yet. Checking again...")
            check_class_availability()
            
    except Exception as e:
        print(f"An error occurred: {e}")

# Close the WebDriver
driver.quit()


