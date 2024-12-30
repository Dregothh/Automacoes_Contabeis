from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
from RPAs import waitElement
import os

# Configure Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1280,800")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

try:
    # Navigate to the login page
    driver.get("https://login.esocial.gov.br/login.aspx")  # Replace with the login URL

    buttonGov = waitElement(driver, By.CSS_SELECTOR, "#login-acoes > div.d-block.mt-3.d-sm-inline.mt-sm-0.ml-sm-3 > p > button")
    buttonGov.click()

    inputId = waitElement(driver, By.CSS_SELECTOR, '#accountId')
    inputId.send_keys('01599639076')
    submit1 = waitElement(driver, By.CSS_SELECTOR, "#enter-account-id")
    submit1.click()
    time.sleep(5)
    driver.save_screenshot("screenshot.png")

    inputPass = waitElement(driver, By.XPATH, '//*[@id="password"]')
    inputPass.send_keys('Ca@263014')
    submit2 = waitElement(driver, By.CSS_SELECTOR, "#submit-button")
    submit2.click()

    # Save a screenshot of the current browser view
    driver.save_screenshot("screenshot.png")

finally:
    # Close the WebDriver
    driver.quit()