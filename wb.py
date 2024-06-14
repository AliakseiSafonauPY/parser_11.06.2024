import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin


options = webdriver.ChromeOptions()
# options.add_argument('--headless=new')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--start-maximized")
service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(options=options, service=service)


url = 'https://www.wildberries.ru/catalog/172623457/detail.aspx'

def parser_wb(url):
    driver.get(url)
    time.sleep(3)
    data = {}

    data['title'] = driver.find_element(By.XPATH, "//div[@class='product-page__grid']//h1").text
    
    price = driver.find_element(By.XPATH, "//div[@class='price-block']//ins").get_attribute('innerText')
    new_price = ' '.join(price.split('\xa0')).strip()
    data['price'] = new_price

    slider_img_list = driver.find_elements(By.XPATH, "//div[@class='product-page__main-slider']//img")
    slider_img_list_src = []

    for e in slider_img_list:
        slider_img_list_src.append(e.get_attribute('src'))

    data['images'] = slider_img_list_src

    clickable = driver.find_element(By.XPATH, "//div[@class='product-page__options']//button[@class='product-page__btn-detail j-wba-card-item j-wba-card-item-show j-wba-card-item-observe']")
    scroll_origin = ScrollOrigin.from_element(clickable)
    ActionChains(driver).scroll_from_origin(scroll_origin, 0, 200).perform()
    time.sleep(1)
    ActionChains(driver).click(clickable).perform()

    time.sleep(1)
    
    list_params = {}

    list_th = driver.find_elements(By.XPATH, "//tbody//th/span/span")
    list_td = driver.find_elements(By.XPATH, "//tbody//td/span")

    for n in range(len(list_th)):
        list_params[f'{list_th[n].text}'] = list_td[n].text

    data['params'] = list_params

    data['description'] = driver.find_element(By.XPATH, "//section[@class='product-details__description option']/p").text

    return data

parser_wb(url)
