import pickle
from selenium import webdriver

def save_cookies(driver, filename):

    with open(filename, "wb") as file:
        pickle.dump(driver.get_cookies(), file)


# Initialize WebDriver
driver = webdriver.Chrome()
driver.get("https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")

input("Press Enter after logging in manually...")

# Save cookies
save_cookies(driver, "linkedin_cookies_account1.pkl")
print(driver.get_cookies())
driver.quit()