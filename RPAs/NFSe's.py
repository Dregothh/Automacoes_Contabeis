from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from RPAs import waitElement
import pandas as pd
from selenium.webdriver.common.keys import Keys


pd.options.display.max_rows = None
pd.options.display.max_columns = None
pd.options.display.width = 99999

df = pd.read_excel("C:/Users/nelso/Desktop/Planilhas Anthony/NFSEs HONORARIOS.xlsx")
print(df)

# def waitElement(driver, by, value):
#     var1 = WebDriverWait(driver, 5).until(
#         EC.element_to_be_clickable((by, value))
#     )
#     return var1


driver = webdriver.Chrome()
driver.get("https://palmaresdosul.govbr.cloud/NFSe.Portal/")

loginBox = driver.find_element(by=By.NAME, value="Usuario")
passBox = driver.find_element(by=By.NAME, value="Senha")
submitButton = driver.find_element(by=By.ID, value="Botao-Entrar")

loginBox.send_keys("80349358087")
passBox.send_keys("36681950")
submitButton.click()

# waitElement(driver, By.XPATH, "//tr[td[contains(text(), 'GLOBAL SERVIÇOS DE ENGENHARIA LTDA')]]//td[button]")
# # Find the row containing the text 'NELSON PEREIRA BRAZ' and select the button within that row
# button = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'GLOBAL SERVIÇOS DE ENGENHARIA LTDA')]]//td[button]")
# button.click()

# driver.get(driver.current_url)
# soup = BeautifulSoup(driver.page_source, 'html.parser')

while True:
    # Wait for the next page button to be clickable
    next_button = waitElement(driver, By.XPATH, "//a[@title='Vai para página seguinte']")

    # Check if the desired button is on the current page
    try:
        # Example: Check for a specific button with text "NELSON PEREIRA BRAZ"
        desired_button = driver.find_element(By.XPATH, "//tr[td[contains(text(), 'FABINHO CONTABEIS LTDA')]]//button")
        if desired_button:
            desired_button.click()
            break
    except:
        # If the button is not found, click the next page button to go to the next page
        next_button.click()
        waitElement(driver, By.XPATH, '//*[@id="grid"]/div[2]/table')
        sleep(1)  # Wait a moment for the next page to load

date = '26122024'
aliquote = '2,0100000000'
dateBox = waitElement(driver, By.NAME, "DataCompetencia")
dateBox.clear()
dateBox.send_keys(date)

for _, row in df.iterrows():
    row = row.tolist()

    while True:
        try:
            documentBox = waitElement(driver, By.NAME, 'DocumentoTomador')
            documentBox.send_keys(f'{row[1]}')
            documentBox.send_keys(Keys.TAB)
            sleep(3)
            closePopup = waitElement(driver, By.CSS_SELECTOR, '#Janela-Modal > div > button.Botao.Botao-Fechar-Modal')
            closePopup.click()
            break
        except:
            print('exception')
            driver.execute_script("location.reload()")
            # driver.find_element(By.TAG_NAME, "body").send_keys(Keys.F5)
            sleep(2)


    serviceBox = waitElement(driver, By.ID, 'Servico')
    serviceBox.send_keys('17.19')

    valueBox = waitElement(driver, By.ID, 'ValorServico')
    valueBox.send_keys(f'{row[2]}')

    descriptionBox = waitElement(driver, By.ID, 'DescricaoServico')
    descriptionBox.send_keys(f'{row[3]}')

    # aliquoteBox = waitElement(driver, By.ID, 'ServicoViewModel_Aliquota')
    # aliquoteBox.send_keys(aliquote)
    # descriptionBox.click()

    submitNFSe = waitElement(driver, By.ID, 'gerarNotaFim')
    submitNFSe.click()

    download = waitElement(driver, By.ID, 'DownloadPDF')
    download.click()
    sleep(1)

    driver.execute_script("location.reload()")

sleep(4)
