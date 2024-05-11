import os
import time
import re

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
    ElementNotInteractableException,
    TimeoutException,
    )

class NewsCrawler():
    '''
    Naver
        section_codes(
            100(정치),
            101(경제),
            102(사회),
            103(생활),
            104(세계),
            165(총선))
    '''
    
    
    def __init__(self,
                 news_site:str,
                 media_companmy_codes:tuple[str],
                 section_codes:tuple[str],
                 collect_count:int
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
        self.options.add_experimental_option("detach", True)
        
        self.webdriver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.wait = WebDriverWait(self.webdriver, 10)  # 10초간 대기
        
        self.DATA_DIR = os.getenv("DATA_DIR")
        self.news_site = news_site
        self.media_companmy_codes = media_companmy_codes
        self.section_codes = section_codes
        self.collect_count = collect_count
        self.content_urls = None
        if self.news_site == "naver":
            self.url = os.getenv("NAVER_NEWS_URL")
            for media_companmy_code in self.media_companmy_codes:
                # for section_code in self.section_codes:
                link_collect_target = f"https://media.naver.com/press/{media_companmy_code}?sid={section_codes}"
                try:
                    self.naver_news_link_collect(media_company_url=link_collect_target)
                except TimeoutException:
                    print("링크 수집 중 TimeoutException 발생")
                    continue
                self.naver_news_crawling()
                
        elif self.news_site == "daum":
            self.url = os.getenv("DAUM_NEWS_URL")
            for media_companmy_code in self.media_companmy_codes:
                # for section_code in self.section_codes:
                print(media_companmy_code)
                link_collect_target = f"https://v.daum.net/channel/{media_companmy_code}/contents"
                try:
                    self.daum_news_link_collect(media_company_url=link_collect_target)
                except TimeoutException:
                    print("링크 수집 중 TimeoutException 발생")
                    continue
                self.daum_news_crawling()
        else:   
            raise "아오 둘중 하나 골라!!"
        
    
    def naver_news_link_collect(self, media_company_url:str):
        self.webdriver.get(media_company_url)
        
        collect_range = range(self.collect_count*3)
        with tqdm(collect_range) as pbar:
            pbar.set_description(f"뉴스 콘텐츠 링크 수집 중..{media_company_url}")
            for _ in pbar:
                try:
                    self.webdriver.execute_script("window.scrollBy(0, 1000);")
                except Exception as e:
                    # 진짜 예외 상황.. 
                    continue
        try:
            sa_text_titles = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.press_edit_news_link")))
        except TimeoutException:
            raise TimeoutException
        else:
            self.content_urls = [content_link.get_attribute("href") for content_link in sa_text_titles[:5]]
        time.sleep(3)
    
    def naver_news_crawling(self):
        for content_url in self.content_urls:
            self.webdriver.get(content_url)
            time.sleep(3)
            title = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[1]/div[1]/div[2]/h2')))
            article = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[1]/div[2]/div[1]')))
            date = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/span')))
            media_company = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'media_end_linked_more_point')))
            
            data = (media_company.text, title.text, date.get_attribute("data-date-time"), article.text)
            self.file_save(data=data)
    
    def daum_news_link_collect(self, media_company_url:str):
        print("아", media_company_url)
        self.webdriver.get(media_company_url)
        
        collect_range = range(self.collect_count*3)
        with tqdm(collect_range) as pbar:
            pbar.set_description(f"뉴스 콘텐츠 링크 수집 중..{media_company_url}")
            for _ in pbar:
                try:
                    self.webdriver.execute_script("window.scrollBy(0, 1000);")
                except Exception as e:
                    # 진짜 예외 상황.. 
                    continue
        try:
            sa_text_titles = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.link_column")))
        except TimeoutException:
            raise TimeoutException
        else:
            self.content_urls = [content_link.get_attribute("href") for content_link in sa_text_titles[:8]
                                 if "#none" not in content_link.get_attribute("href")]
        time.sleep(3)
    
    def daum_news_crawling(self):
        for content_url in self.content_urls:
            self.webdriver.get(content_url)
            time.sleep(3)
            title = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tit_view')))
            article = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'article_view')))
            date = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'num_date')))
            media_company = self.wait.until(EC.presence_of_element_located((By.ID, 'kakaoServiceLogo')))
            
            data = (media_company.text, title.text, date.text, article.text)
            self.file_save(data=data)
    
    def file_save(self, data:list,):
        columns = "media_company, title date article".split()
        media_company, title, _, _ = data
        
        only_korean = re.compile("[^ㄱ-ㅎㅏ-ㅣ가-힣]+")
        title = re.sub(only_korean, "", title)
        file_name = f'{self.news_site.upper()}_{title}_{media_company}.xlsx'
        download_path = os.path.join(self.DATA_DIR, self.news_site, media_company, file_name).replace('\\', '/')
        
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        pd.DataFrame(
            data=[data],
            columns=columns).to_excel(download_path)
    
    @staticmethod
    def naver_media_company_info_to_csv():
        from bs4 import BeautifulSoup
        with open('naver_media_companys.html', 'r', encoding='utf8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            media_company_links = [(x.select_one('strong').text, x["href"]) for x in soup.select("ul li a.press_list_logo_item")]
            print(media_company_links)
            pd.DataFrame(data=media_company_links, columns=["media_company", "url"]).to_csv("naver_media_company.csv", index=False)
    
    @staticmethod
    def daum_media_company_info_to_csv():
        from bs4 import BeautifulSoup
        with open('daum_media_companys.html', 'r', encoding='utf8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            media_company_links = [(x.text, x["href"]) for x in soup.select("ul li a.link_txt")]
            pd.DataFrame(data=media_company_links, columns=["media_company", "url"]).to_csv("daum_media_company.csv", index=False)
            
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # NewsCrawler.daum_media_company_info_to_csv()
    # quit()
    
    naver_media_company = pd.read_csv("naver_media_company.csv")
    naver_media_companmy_codes = [os.path.basename(url) for url in naver_media_company["url"].to_list()] 
    
    daum_media_company = pd.read_csv("daum_media_company.csv")
    daum_media_companmy_codes = [os.path.basename(url) for url in daum_media_company["url"].to_list()]

    mcodes = list(daum_media_companmy_codes)[9:]
    nc = NewsCrawler(
        news_site='daum',
        media_companmy_codes=daum_media_companmy_codes,
        section_codes=("100"),
        collect_count=1
    )
    
    

# 크롤러:
#     입력:
#         a=사이트명:str naver/daum
#         b=무슨 카테고리 크롤링 할 건지?(옵션, 기본: 홈):tuple(str)
#         c=카테고리 당 몇개 수집할 건지(옵션, 기본: 10개):int
#     출력:
#         c=의 갯수만큼 csv 저장
    
#     동작:
#         예외처리:
#             a 접속
#             b 내부 값의 카테고리를
#             c만큼씩 수집:
#                 1. 스크롤
#                 2. 뉴스 컨텐츠 접속
#                 3. 수집(csv 저장)
#                     data/제목-출판사
#                     collect_date/제목-출판사.txt(XXXX 이 떄 수집됨)
#                 print(수집 완료 메시지)
#         예외:
#             예외 내용별로 처리
        
# 크롤링 완료

# 데이터 병합

