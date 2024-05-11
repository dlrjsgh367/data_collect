import os
from tempfile import mkdtemp

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

global section_dict
section_dict = {
    "주요뉴스": "",
    "정치": "100",
    "경제": "101",
    "사회": "102",
    "생활": "103",
    "세계": "104",
    "it": "105",
    "사설/칼럼": "110",
    "총선": "165",
}

def web_driver_options():
    chrome_option_object = webdriver.ChromeOptions()
    # chrome_option_object.add_argument('--headless')
    chrome_option_object.add_argument('--no-sandbox')
    chrome_option_object.add_argument("--disable-gpu")
    chrome_option_object.add_argument("--window-size=1280x1696")
    chrome_option_object.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
    chrome_option_object.add_argument("single-process")
    chrome_option_object.add_argument("--disable-dev-shm-usage")
    chrome_option_object.add_argument("--disable-dev-tools")
    chrome_option_object.add_argument("--no-zygote")
    chrome_option_object.add_argument(f"--user-data-dir={mkdtemp()}")
    chrome_option_object.add_argument(f"--data-path={mkdtemp()}")
    chrome_option_object.add_argument(f"--disk-cache-dir={mkdtemp()}")
    chrome_option_object.add_experimental_option('excludeSwitches', ['enable-logging'])
    chrome_option_object.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_option_object.add_experimental_option("useAutomationExtension", False)
    # chrome_option_object.add_experimental_option("detach", True)
    return chrome_option_object

def web_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager("124.0.6367.119").install()), options=web_driver_options())
    return driver

def naver_url_generator(base_url, media_company_no, section_no):
    if section_no == '':
        url = f"{base_url}/press/{media_company_no}"
    else:
        url = f"{base_url}/press/{media_company_no}?sid={section_no}"
    return url

def main():
    # target = "https://media.naver.com/press/277"
    url = "https://media.naver.com/press/666"
    
    driver = web_driver()
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    element = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'press_section_tab_txt')))
    collected_section_no = [x.text for x in element]
    print(collected_section_no)
    
    available_section_no = [section_dict.get(i) for i in collected_section_no if section_dict.get(i) is not None]
    print(available_section_no)
    
    for section_no in available_section_no:
        print(naver_url_generator(url,"666", section_no))

def naver_test():
    pass
if __name__ == "__main__":
    main()
    quit()
    url = "https://media.naver.com"

    
    collected_section_no = []
    available_section_no = [section_dict.get(i) for i in x if section_dict.get(i) is not None]
    for i in y:
        url = naver_url_generator(url,"044", i)
        print(url)
        