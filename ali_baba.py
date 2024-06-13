import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


def ali_baba_scrapping(url):
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless=new')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(options=options, service=service)

    list_of_subcategories = []
    list_of_products = []
    result = {}

    def check_exists_by_xpath(by, xpath):
        try:
            driver.find_element(by, xpath)
        except NoSuchElementException:
            return False
        return True
    
    def get_subcategory(url):

        driver.get(url)
        
        list_a = driver.find_elements(By.XPATH, "//div[@class='ch-menu']//a")
        list_p = driver.find_elements(By.XPATH, "//div[@class='ch-menu']//a/p")

        for n in range(len(list_a)):
            list_of_subcategories.append({'href': list_a[n].get_attribute("href"), 'category': list_p[n].text.strip()})

    def get_products(url):
        driver.get(url['href'])

        time.sleep(1)

        if not check_exists_by_xpath(By.CLASS_NAME, "channel-common-footer"):
            div_to_product = driver.find_element(By.XPATH, "//div[@class='tab-container']//a")
            ActionChains(driver).click(div_to_product).perform()
            time.sleep(1)
        
        time.sleep(1)

        footer = driver.find_element(By.CLASS_NAME, "channel-common-footer")
        delta_y = footer.rect['y']
        delta_y_old = footer.rect['y']

        while True:
            ActionChains(driver).scroll_by_amount(0, int(delta_y)).perform()
            time.sleep(2)
            footer = driver.find_element(By.CLASS_NAME, "channel-common-footer")
            delta_y = footer.rect['y']
            if delta_y_old == delta_y:
                break
            delta_y_old = delta_y

        list_a = driver.find_elements(By.XPATH, "//div[@class='cate1688-snOffer']//div[@class='list']//a[@class='offer']")

        for e in list_a:
            try:
                list_of_products.append({'href': e.get_attribute("href"), 'category': url['category']})
            except StaleElementReferenceException:
                pass

    def get_product_info(url):
        data = {}

        data['link'] = url['href']
        data['category'] = url['category']
        
        driver.get(url['href'])

        time.sleep(2)

        if check_exists_by_xpath(By.ID, "nc_1_n1z"):
            
            draggable = driver.find_element(By.ID, "nc_1_n1z")

            ActionChains(driver).drag_and_drop_by_offset(draggable, 200, 0).perform()
            time.sleep(3)
            ActionChains(driver).drag_and_drop_by_offset(draggable, 400, 0).perform()
            time.sleep(2)

            driver.refresh()
        
        time.sleep(2)

        footer = driver.find_element(By.ID, "shop-container-footer")
        delta_y = footer.rect['y']
        delta_y_old = footer.rect['y']

        while True:
            ActionChains(driver).scroll_by_amount(0, int(delta_y)).perform()
            time.sleep(2)
            footer = driver.find_element(By.ID, "shop-container-footer")
            delta_y = footer.rect['y']
            if delta_y_old == delta_y:
                break
            delta_y_old = delta_y

        data['title'] = driver.find_element(By.XPATH, "//div[@class='title-text']").text
        color_or_size = {}

        list_names = driver.find_elements(By.XPATH, "//div[@class='sku-module-horizon-list']//div[@class='sku-item-left']//div[@class='sku-item-name']")
        list_prices = driver.find_elements(By.XPATH, "//div[@class='sku-module-horizon-list']//div[@class='sku-item-left']//div[@class='discountPrice-price']")

        for n in range(len(list_names)):
            color_or_size[f'{list_names[n].get_attribute('innerHTML')}'] = list_prices[n].get_attribute('innerHTML')

        data['color or size'] = color_or_size

        slider_img_list = driver.find_elements(By.XPATH, "//div[@class='detail-gallery-turn']//img[@class='detail-gallery-img']")
        slider_img_list_src = []

        for e in slider_img_list:
            slider_img_list_src.append(e.get_attribute('src'))

        data['img_list_slider'] = slider_img_list_src
        data['weight(净含量)'] = 'None'

        weight_name = driver.find_elements(By.XPATH, "//div[@class='od-pc-attribute']//span[@class='offer-attr-item-name']")
        weight_value = driver.find_elements(By.XPATH, "//div[@class='od-pc-attribute']//span[@class='offer-attr-item-value']")

        for q in range(len(weight_name)):
            if weight_name[q].text == '净含量':
                data['weight(净含量)'] = weight_value[q].text

        img_detail = driver.find_elements(By.XPATH, "//div[@class='detail-desc-module']//img[@class='desc-img-loaded']")
        img_detail_list = []

        for i in img_detail:
            img_detail_list.append(i.get_attribute('src'))
        data['img_detail'] = img_detail_list

        list_p = driver.find_elements(By.XPATH, "//div[@class='od-pc-detail-description']//p/span")
        list_p_text = []

        for t in list_p:
            if t.text:
                list_p_text.append(t.text)
        if len(list_p_text) > 0:
            data['text_detail'] = ', '.join(list_p_text)
        else:
            data['text_detail'] = 'None'
        
        result[f'{url['href']}'] = data

    get_subcategory(url)

    if len(list_of_subcategories) > 0:
        for subcat in list_of_subcategories:
            get_products(subcat)
    else:
        print('there may be errors in the input parameter')
        return
    
    if len(list_of_products) > 0:
        for prod in list_of_products:
            get_product_info(prod)
    else:
        print('no products found')

    return result
            

ali_baba_scrapping('https://mei.1688.com/?spm=a260k.dacugeneral.home2019category.20.38c235e4NmX2P8')