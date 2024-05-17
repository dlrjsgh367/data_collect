import re
import os
import time

import pandas as pd
from tqdm import tqdm
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from web_driver import WebDriver
from interface import NewsCrawlerInterface



class DaumNewsCrawler(WebDriver, NewsCrawlerInterface):
    """
    daum 뉴스 기사를 언론사별로 크롤링 하는 클래스
    """
    def __init__(self, chrome_version, scroll_range, press_link_list, press_name_list):
        super().__init__(chrome_version)
        self.scroll_range = range(scroll_range)
        self.press_link_list = press_link_list
        self.press_name_list = press_name_list
        self.content_link_list = []
        self.press_name = ""
        
        self.data_dir = os.getenv("DATA_DIR")
        self.columns = "media_company, title date article".split()
        self.news_crawler()
        
    def news_crawler(self):
        for press_link, press_name in zip(self.press_link_list, self.press_name_list):
            self.press_name = press_name
            self.news_content_link_collect(press_link)
            self.news_content_parsing()
    
    def news_content_link_collect(self, press_link):
        # 전체뉴스 섹션
        press_link = f'{press_link}/contents'
        
        # 다음 언론사 메인 페이지 접근
        self.webdriver.get(press_link)
        
        # 뉴스 컨텐츠 링크 수집
        content_link_list = []
        with tqdm(self.scroll_range) as pbar:
            pbar.set_description(f"{self.press_name} 컨텐츠 링크 수집 중")
            for _ in pbar:
                self.webdriver.execute_script("window.scrollBy(0, 1000);")
        
        sa_text_titles = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.link_column")))
        content_link_list.extend([content_link.get_attribute("href") for content_link in sa_text_titles if "#none" not in content_link.get_attribute("href")])
        time.sleep(3)
        self.content_link_list = content_link_list
    
    def news_content_parsing(self):
        with tqdm(self.content_link_list) as content_link_list:
            content_link_list.set_description(f"{self.press_name} 컨텐츠 파싱 중")            
            for content_link in content_link_list:

                self.webdriver.get(content_link)
                
                title = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tit_view')))
                article = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'article_view')))
                date = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'num_date')))
                media_company = self.wait.until(EC.presence_of_element_located((By.ID, 'kakaoServiceLogo')))
                
                data = (media_company.text, title.text, date.text, article.text)
                self.file_save(data=data)
                time.sleep(3)

    def file_save(self, data):
        media_company, title, _, _ = data
        
        only_korean = re.compile("[^ㄱ-ㅎㅏ-ㅣ가-힣]+")
        title = re.sub(only_korean, "", title)
        
        file_name = f'DAUM_{title}_{media_company}.xlsx'
        download_path = os.path.join(self.data_dir, 'TEST', media_company, file_name).replace('\\', '/')
        
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        pd.DataFrame(data=[data],columns=self.columns).to_excel(download_path)
        print(download_path)