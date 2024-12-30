from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# driver = webdriver.Chrome()
# driver.get("https://palmaresdosul.govbr.cloud/NFSe.Portal/")
# print(driver.title)

def waitElement(driver, by, value, timeout=5):
    var1 = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    return var1
