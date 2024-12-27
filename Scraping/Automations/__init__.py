from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://palmaresdosul.govbr.cloud/NFSe.Portal/")
print(driver.title)