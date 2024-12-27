from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time

# Create Firefox options
options = Options()
options.set_preference("security.default_personal_cert", "Ask Every Time")  # Ensure certificate dialog appears

# Path to your geckodriver
geckodriver_path = "C:/Users/nelso/Downloads/ZZZZZZZZZZ/geckodriver.exe"

# Set up Firefox driver with the custom profile
driver = webdriver.Firefox(service=Service(geckodriver_path), options=options)

driver.get('https://login.esocial.gov.br/login.aspx')
time.sleep(5)