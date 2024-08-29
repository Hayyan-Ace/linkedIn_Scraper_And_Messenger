import time
import pickle
import random
import os
import schedule
import csv
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Constants
LINKEDIN_URL = "https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin"
CurrentMessagingAccount = ""

log_file = 'message_log.csv'
accounts_message_and_headline_file = 'accounts.csv'  # Replace with your actual CSV file path
directory = 'AccountsCookiesPickle'

BODY_TEMPLATE = "Hi {first_name}, hope you’re doing well. Looks like you’re crushing it with your AI automation business. I specialize in lead generation for LinkedIn and I’d like to bring you 2-5 additional clients to your business every month - contractually guaranteed. Open to hearing more about it?"


def load_cookies(driver, filename):
    with open(filename, 'rb') as file:
        cookies = pickle.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)


# Initialize the WebDriver (use your preferred WebDriver and its path)
def load_and_use_cookies(account_name):
    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome()
    driver.get('https://www.linkedin.com/')
    time.sleep(2)
    # Load cookies from the file
    load_cookies(driver, f'{directory}/{account_name}.pkl')

    # Refresh the page to apply the cookies
    driver.refresh()
    time.sleep(2)
    return driver


def next_page(driver):
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
        next_button = driver.find_element(By.XPATH, "//button[@aria-label='Next']")
        next_button.click()
    except Exception as e:
        print(f"Error clicking 'Next' button: {e}")

def log_to_csv(profile_url, account_url, log_file):
    with open(log_file, mode='a', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(account_url)



def setup_driver(profile_path):
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={profile_path}")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def send_messages(driver, search_url, body_template, subject_lines, log_file, num_messages):
    driver.get(search_url)
    time.sleep(3)
    messages_sent = 0

    while messages_sent < num_messages:
        profile_links = set()
        title_line_spans = driver.find_elements(By.CLASS_NAME, 'entity-result__title-line')
        for span in title_line_spans:
            a_elements = span.find_elements(By.TAG_NAME, 'a')
            for a in a_elements:
                href = a.get_attribute('href')
                if href and "https://www.linkedin.com/in/" in href:
                    profile_links.add(href)

        for profile_url in profile_links:
            if messages_sent >= num_messages:
                break

            # Switch to the second tab and open the profile URL
            driver.switch_to.window(driver.window_handles[1])
            driver.get(profile_url)

            # Extract the full name and first name
            full_name = driver.find_element(By.TAG_NAME, 'h1').text
            first_name = full_name.split()[0]

            # Prepare the message
            message_body = body_template
            message_body = message_body.replace("{first_name}", first_name)

            message_subject = random.choice(subject_lines)

            # Try to find and click the message button
            try:
                time.sleep(2)
                message_button = driver.find_element(By.XPATH, "//main//button[contains(@aria-label, 'Message')]")
                time.sleep(2)
                message_button.click()
            except:
                print(f"Could not find message button for {profile_url}")
                continue

            # Check for the upsell modal
            # Send message as connection request
            try:
                time.sleep(3)
                # Escaping or crossing the screen that comes after Direct Message attempts are exhausted for the month.
                dismiss_button = driver.find_element(By.XPATH,
                                                     "//button[@class='artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view artdeco-modal__dismiss']")
                dismiss_button.click()
                time.sleep(2)

                # Checking if the Connection button is present on the main screen by default.
                try:
                    connect_button = driver.find_element(By.XPATH,
                                                         "//button[@class='artdeco-button artdeco-button--2 artdeco-button--primary ember-view pvs-profile-actions__action']")
                    driver.execute_script("arguments[0].click();", connect_button)
                except:
                    print("Connect button is not present on the main screen by default")

                # Clicking the "More" Button to get to Connect
                try:
                    moreButton = driver.find_element(By.XPATH,
                                                     "//button[@aria-label='More actions' and contains(@class, 'artdeco-dropdown__trigger') and .//span[text()='More']]")
                    driver.execute_script("arguments[0].click();", moreButton)

                    clickOnConnect = driver.find_element(By.XPATH,
                                                         f"//div[@aria-label='Invite {full_name} to connect' and contains(@class, 'artdeco-dropdown__item') and .//span[text()='Connect']]")
                    driver.execute_script("arguments[0].click();", clickOnConnect)
                except:
                    print("Connection already sent by this LinkedIn profile")

                add_note_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Add a note')]")
                driver.execute_script("arguments[0].click();", add_note_button)

                # connect_button = driver.find_element(By.XPATH, "//button[@class='artdeco-button artdeco-button--2 artdeco-button--primary ember-view pvs-profile-actions__action']")
                # driver.execute_script("arguments[0].click();", connect_button)

                time.sleep(2)
                body_input = driver.find_element(By.XPATH, "//textarea[@name='message']")

                    # Please add a new message body as LinkedIn allows 200 characters if message is being this way
                body_input.send_keys(message_body)

                time.sleep(1)
                send_invitation_button = driver.find_element(By.XPATH, "//button[@aria-label='Send invitation']")
                driver.execute_script("arguments[0].click();", send_invitation_button)
                time.sleep(2)
                # close_button = driver.find_element(By.XPATH, "//button[@aria-label='Dismiss' and contains(@class='artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view artdeco-modal__dismiss')]")
                # driver.execute_script("arguments[0].click();", close_button)
                messages_sent += 1
                log_to_csv(profile_url, driver.current_url, log_file)
                time.sleep(2)
            except Exception as e:
                print("Either request wa already sent by this profile or incase of error check the below message")
                print(e)
                time.sleep(2)

                # Send direct message
                try:
                    message_modal = driver.find_element(By.XPATH,
                                                        f"//div[contains(@class, 'msg-convo-wrapper') and contains(., '{full_name}') and contains(., 'New message')]")
                    body_input = message_modal.find_element(By.CLASS_NAME, "msg-form__contenteditable")
                    body_input.send_keys(message_body)
                    time.sleep(0.5)
                    subject_input = message_modal.find_element(By.XPATH, "//input[@name='subject']")
                    subject_input.send_keys(message_subject)
                    send_button = message_modal.find_element(By.XPATH, "//button[@type='submit']")
                    send_button.click()
                    print("Direct message sent")
                    messages_sent += 1
                    log_to_csv(profile_url, driver.current_url, log_file)
                    time.sleep(2)
                except Exception as e:
                    print(f"Failed to send direct message to {profile_url}: {e}")
            try:
                time.sleep(2)
                close_button_svg = driver.find_element(By.XPATH,
                                                       "//button[@class='msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']")

                # close_button_svg = message_modala.find_element(By.XPATH,
                #   f"//button[contains(@class,'msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view']")
                # a = "msg-overlay-bubble-header__control artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--1 artdeco-button--tertiary ember-view"
                # Perform actions on the close button SVG
                close_button_svg.click()
            except Exception as e:
                print(e)
                time.sleep(2)

        profile_links.clear()

        driver.switch_to.window(driver.window_handles[0])
        time.sleep(0.5)
        next_page(driver)
        time.sleep(5)


def read_csv(driver, file_path, account_name):
    accounts = []
    with (open(file_path, mode='r', newline='', encoding='utf-8') as csvfile):
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['account_name'] == account_name:
                accounts.append(row)


    return accounts




def start():
    # Initialize as variables to default
    messages_per_day = 0
    custom_message = []
    headlines = []
    SEARCH_URL = None
    for account_file in os.listdir(directory):
        if account_file.endswith('.pkl'):
            account_name = account_file.replace('.pkl', '')
            print(f"Loading cookies for account: {account_name}")
            driver = load_and_use_cookies(account_name)

            accounts = read_csv(driver, accounts_message_and_headline_file, account_name)
            for account in accounts:
                custom_message = account['custom_message']
                headlines = account['headlines'].split('\n')  # Split headlines by newline
                messages_per_day = int(account['messages_per_day'])
                SEARCH_URL = account['searchURL']

            # Refresh to apply cookies and ensure the session is active

            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)
            send_messages(driver, SEARCH_URL, custom_message, headlines, log_file, messages_per_day)
            driver.quit()

        time.sleep(15)


start()