import os
import re
import time
from tempfile import mkdtemp
from abc import ABC, abstractmethod

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

class WebDriver:
    """
    셀레니움 크롬 웹 드라이버
    """
    def __init__(self, chrome_version):
        """
        자신의 크롬 버전을 입력
        e. g) '124.0.6367.119'
        """
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
        
        self.webdriver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_version).install()), options=self.options)
        self.wait = WebDriverWait(self.webdriver, 10)

class NewsCrawlerInterface(ABC):
    @abstractmethod
    def news_crawler(self):
        pass
    
    @abstractmethod
    def news_content_link_collect(self):
        pass
    
    @abstractmethod
    def news_content_parsing(self):
        pass
    
    @abstractmethod
    def file_save(self):
        pass
    
class NaverNewsCrawler(WebDriver, NewsCrawlerInterface):
    """
    daum 뉴스 기사를 언론사별로 크롤링 하는 클래스
    """
    def __init__(self, chrome_version, scroll_range, press_link_list, press_name_list):
        """
        입력
            크롬 브라우저 버전
            언론사 메인 페이지 링크 목록
            언론사명 목록
        """
        # 부모 클래스 WebDriver에서 웹 드라이버가 실행됨
        super().__init__(chrome_version)
        self.scroll_range = range(scroll_range)
        self.press_link_list = press_link_list
        self.press_name_list = press_name_list
        self.content_link_list = []
        self.press_name = ""
        
        # 데이터 출력 경로
        self.data_dir = os.getenv("DATA_DIR")
        # 데이터 칼럼
        self.columns = "press title date article".split()
        # 네이버 섹션 딕셔너리
        self.section_dict = {
            "주요뉴스": "",
            "정치": "100",
            "경제": "101",
            "사회": "102",
            "생활": "103",
            "세계": "104",
            "it": "105",
            "사설/칼럼": "110",
            "총선": "165"
        }
        # 네이버 섹션 딕셔너리의 k-v를 스왑한 딕셔너리
        self.reverse_section_dict = dict((v,k) for k,v in self.section_dict.items())
        
        # 크롤링 시작
        self.news_crawler()
        
    def news_crawler(self):
        """
        언론사 메인 페이지 링크 목록, 언론사명 목록을 zip으로 묶고 for-each
            self.press_name 변수에 press_name 주소를 할당
            self.news_content_link_collect()에 언론사 메인 페이지 링크를 전달함
        """
        for press_link, press_name in zip(self.press_link_list, self.press_name_list):
            self.press_name = press_name
            self.news_content_link_collect(press_link)
            self.news_content_parsing()
            
    
    def news_content_link_collect(self, press_link):
        """
        []
        
        [링크 수집 로직]
        1. 페이지를 스크롤한다
            a. html에 노출되는 뉴스 컨텐츠가 증가한다
        2. 스크롤이 끝난다
        3. html에 존재하는 모든 컨텐츠 정보를 파싱한다
        4. 3.에서 href 값만 가져온 후 content_link_list에 extend 한다.
        """
        # 네이버 언론사 메인 페이지 접근
        self.webdriver.get(press_link)
        
        # 사용 가능한 섹션이 있는지 확인
        content_section_list = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'press_section_tab_txt')))
        content_section_code_list = [x.text for x in content_section_list]
        available_section_code_list = [self.section_dict.get(x) for x in content_section_code_list
                                       if self.section_dict.get(x) is not None]
        
        # 사용 가능한 섹션 코드로 뉴스 컨텐츠 링크 생성
        available_section_link_list = [self.content_link_generator(press_link, x) for x in available_section_code_list]
        
        # 섹션 별로 뉴스 컨텐츠 링크 수집
        content_link_list = []
        for (available_section_link, section_code) in available_section_link_list:
            self.webdriver.get(available_section_link)
            with tqdm(self.scroll_range) as pbar:
                pbar.set_description(f"{self.press_name} {self.reverse_section_dict.get(section_code)} 컨텐츠 링크 수집 중")
                for _ in pbar:
                    self.webdriver.execute_script("window.scrollBy(0, 1000);")

            sa_text_titles = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.press_edit_news_link")))
            content_link_list.extend([content_link.get_attribute("href") for content_link in sa_text_titles])
            time.sleep(3)
        
        # content_link_list 값을 self.content_link_list에 할당
        self.content_link_list = content_link_list
        
    def content_link_generator(self, press_link, section_code):
        if section_code != '':
            press_link = f'{press_link}?sid={section_code}'
        return (press_link, section_code)
    
    def news_content_parsing(self):
        with tqdm(self.content_link_list) as content_link_list:
            content_link_list.set_description("네이버 뉴스 컨텐츠 파싱")            
            for content_link in content_link_list:

                self.webdriver.get(content_link)
                
                title = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[1]/div[1]/div[2]/h2')))
                article = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[1]/div[2]/div[1]')))
                date = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/span')))
                media_company = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'media_end_linked_more_point')))
                
                data = (media_company.text, title.text, date.get_attribute("data-date-time"), article.text)
                self.file_save(data)
                time.sleep(3)

    def file_save(self, data):
        media_company, title, _, _ = data
        
        only_korean = re.compile("[^ㄱ-ㅎㅏ-ㅣ가-힣]+")
        title = re.sub(only_korean, "", title)
        
        file_name = f'NAVER_{title}_{media_company}.xlsx'
        download_path = os.path.join(self.data_dir, 'TEST', media_company, file_name).replace('\\', '/')
        
        os.makedirs(os.path.dirname(download_path), exist_ok=True)
        pd.DataFrame(data=[data],columns=self.columns).to_excel(download_path)
        print(download_path)

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

def main():
    press_dataframe = pd.read_csv(r"C:\Users\HAMA\code\workspace\Projects\data_collect\news\daum_media_company.csv")
    press_link_list = press_dataframe["url"].tolist()
    press_name_list = press_dataframe["media_company"].tolist()
    press_link_list = ["https://v.daum.net/channel/8"]
    DaumNewsCrawler(
        chrome_version = "124.0.6367.119",
        press_link_list = press_link_list,
        press_name_list = press_name_list,
    )

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_env = load_dotenv()
    print(load_env)
    main()