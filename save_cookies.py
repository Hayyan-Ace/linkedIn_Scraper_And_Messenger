import os
import pickle
from selenium import webdriver

# Create the AccountsCookiesPickle directory if it doesn't exist
directory = 'AccountsCookiesPickle'
if not os.path.exists(directory):
    os.makedirs(directory)

def save_cookies(driver, filename):
    cookies = driver.get_cookies()
    with open(filename, 'wb') as file:
        pickle.dump(cookies, file)

# Initialize the WebDriver (use your preferred WebDriver and its path)
driver = webdriver.Chrome()

# Navigate to LinkedIn (or the site you need)
driver.get('https://www.linkedin.com/')

# Manually log in to LinkedIn using the opened browser window
account_name = input("Enter the account name: ")
input("Log in to the account and press Enter to save cookies...")

# Save cookies for the provided account name
save_cookies(driver, f'{directory}/{account_name}.pkl')

driver.quit()
