import os
import re
import time
from tempfile import mkdtemp

import pandas as pd
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    TimeoutException,
    )


class NewsCrawler():
    
    base_media_company_url = "https://media.naver.com/press"
    naver_section_dict = {
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
    
    DATA_DIR = "./Data/"
    def __init__(self,
                site_name: str,  # 크롤링할 사이트 (네이버 또는 다음)
                media_company_codes: tuple[str],  # 크롤링할 언론사 코드 목록
                scroll_range: int  # 스크롤 범위(3배)
                ):
        
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1280x1696")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36")
        self.options.add_argument("single-process")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-dev-tools")
        self.options.add_argument("--no-zygote")
        self.options.add_argument(f"--user-data-dir={mkdtemp()}")
        self.options.add_argument(f"--data-path={mkdtemp()}")
        self.options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        self.options.add_experimental_option('excludeSwitches', ['enable-logging'])
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        self.options.add_experimental_option("detach", False)
        
        self.webdriver = webdriver.Chrome(service=Service(ChromeDriverManager("124.0.6367.119").install()), options=self.options)
        self.wait = WebDriverWait(self.webdriver, 10)  # 10초간 대기
        
        self.site_name = site_name
        self.media_company_codes = media_company_codes
        self.scroll_range = scroll_range
        
        self.content_urls = None
        
        if self.site_name == "naver":
            self.crawl_naver_news()
        else:   
            raise "아오 둘중 하나 골라!!"
        
    def crawl_naver_news(self):
        for media_companmy_code in self.media_company_codes:
            media_company_url = f"{self.base_media_company_url}/{media_companmy_code}"
            self.naver_news_link_collect(
                media_companmy_code=media_companmy_code,
                link_collect_target=media_company_url
                )
            self.naver_news_crawling()
    
    def naver_news_link_collect(self, media_companmy_code:str, link_collect_target:str):
        naver_section_dict = dict((v,k) for k,v in self.naver_section_dict.items())
    
        self.webdriver.get(link_collect_target)
        
        collected_section = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'press_section_tab_txt')))
        collected_section_no = [x.text for x in collected_section]
        available_section_no = [self.naver_section_dict.get(i) for i in collected_section_no if self.naver_section_dict.get(i) is not None]
        section_urls = [(x, self.naver_url_generator(media_companmy_code=media_companmy_code, section_no=x)) for x in available_section_no]
        
        content_urls = []
        for section_no, section_url in section_urls:
            self.webdriver.get(section_url)
            collect_range = range(self.scroll_range*3)
            with tqdm(collect_range) as pbar:
                pbar.set_description(f"[{naver_section_dict.get(section_no)}] 섹션 링크 수집")
                for _ in pbar:
                    self.webdriver.execute_script("window.scrollBy(0, 1000);")

                sa_text_titles = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.press_edit_news_link")))
            content_urls.extend([content_link.get_attribute("href") for content_link in sa_text_titles])
            time.sleep(3)

        self.content_urls = content_urls
        
    def naver_url_generator(self, media_companmy_code, section_no):
        if section_no == '':
            url = f"{self.base_media_company_url}/{media_companmy_code}"
        else:
            url = f"{self.base_media_company_url}/{media_companmy_code}?sid={section_no}"
        return url

    def naver_news_crawling(self):
        with tqdm(self.content_urls) as content_urls:
            content_urls.set_description("link collecting... ")            
            for content_url in content_urls:

                self.webdriver.get(content_url)
                
                title = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[1]/div[1]/div[2]/h2')))
                article = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[1]/div[2]/div[1]')))
                date = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/span')))
                media_company = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'media_end_linked_more_point')))
                
                data = (media_company.text, title.text, date.get_attribute("data-date-time"), article.text)
                self.file_save(data=data)
                time.sleep(3)

    def file_save(self, data:list):
        columns = "media_company, title date article".split()
        media_company, title, _, _ = data
        
        only_korean = re.compile("[^ㄱ-ㅎㅏ-ㅣ가-힣]+")
        title = re.sub(only_korean, "", title)
        file_name = f'{self.site_name.upper()}_{title}_{media_company}.xlsx'
        download_path = os.path.join(self.DATA_DIR, self.site_name, media_company, file_name).replace('\\', '/')
        print(download_path)
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        pd.DataFrame(
            data=[data],
            columns=columns).to_excel(download_path)
        
def main(site_name:str) -> tuple[str]:
    if site_name not in ["naver"]:
        return None
    
    media_company_table = pd.read_csv(f"{site_name}_media_company.csv")
    media_company_codes = [os.path.basename(url) for url in media_company_table["url"].tolist()]
    NewsCrawler(
        site_name=site_name,
        media_company_codes=media_company_codes,
        scroll_range=10
    )
    
if __name__ == "__main__":
    # from dotenv import load_dotenv
    # load_dotenv()
    main("naver")