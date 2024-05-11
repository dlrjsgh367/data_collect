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
    
    def __init__(self,
                site_name: str,  # 크롤링할 사이트 (네이버 또는 다음)
                media_company_codes: tuple[str],  # 크롤링할 언론사 코드 목록
                section_codes: tuple[str],  # 크롤링할 섹션 코드 목록
                scroll_range: int  # 수집할 페이지 수
                ):
        
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('--headless')+
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
        self.site_name = site_name
        self.media_company_codes = media_company_codes
        self.section_codes = section_codes
        self.scroll_range = scroll_range
        
        self.content_urls = None
        
        if self.site_name == "naver":
            self.url = os.getenv("NAVER_NEWS_URL")
            self.crawl_naver_news()
        elif self.site_name == "daum":
            self.url = os.getenv("DAUM_NEWS_URL")
            self.crawl_daum_news()
        else:   
            raise "아오 둘중 하나 골라!!"
        
    def crawl_naver_news(self):
        for media_companmy_code in self.media_company_codes:
            # for section_code in self.section_codes:
            # link_collect_target = f"https://media.naver.com/press/{media_companmy_code}?sid={self.section_codes}"
            link_collect_target = f"https://media.naver.com/press/{media_companmy_code}"
            try:
                self.naver_news_link_collect(media_company_url=link_collect_target)
                print("음")
            except Exception as e:
                with open("err_record.txt", 'a', encoding='utf8') as f:
                    f.write(str(e) + '\n' + link_collect_target)
                print("링크 수집 중 예외 발생")
                continue
            else:
                self.naver_news_crawling()
                print("오")
        
    def crawl_daum_news(self):
        for media_companmy_code in self.media_company_codes:
            link_collect_target = f"https://v.daum.net/channel/{media_companmy_code}/contents"
            try:
                self.daum_news_link_collect(media_company_url=link_collect_target)
                print("음")
            except Exception as e:
                with open("err_record.txt", 'a', encoding='utf8') as f:
                    f.write(str(e) + '\n' + link_collect_target)
                print("링크 수집 중 예외 발생")
                continue
            else:
                self.daum_news_crawling()
                print("오")
            quit()
    
    def naver_news_link_collect(self, media_company_url:str):
        self.webdriver.get(media_company_url)
        
        collect_range = range(self.scroll_range*3)
        with tqdm(collect_range) as pbar:
            pbar.set_description(f"link collecting.. ")
            for _ in pbar:
                try:
                    self.webdriver.execute_script("window.scrollBy(0, 1000);")
                except Exception as e:
                    raise e
        try:
            sa_text_titles = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.press_edit_news_link")))
        except Exception as e:
            raise e
        else:
            self.content_urls = [content_link.get_attribute("href") for content_link in sa_text_titles[:5]]
            print(self.content_urls)
    
    def naver_news_crawling(self):
        for content_url in self.content_urls:
            print(content_url)
            self.webdriver.get(content_url)
            
            title = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[1]/div[1]/div[2]/h2')))
            article = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[1]/div[2]/div[1]')))
            date = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/span')))
            media_company = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'media_end_linked_more_point')))
            
            data = (media_company.text, title.text, date.get_attribute("data-date-time"), article.text)
            self.file_save(data=data)
            time.sleep(3)
    
    def daum_news_link_collect(self, media_company_url:str):
        self.webdriver.get("https://v.daum.net/channel/259/contents")
        print("아")
        collect_range = range(self.scroll_range*3)
        with tqdm(collect_range) as pbar:
            pbar.set_description(f"link collecting..")
            for _ in pbar:
                try:
                    self.webdriver.execute_script("window.scrollBy(0, 1000);")
                    print("스크롤 진행")
                except Exception as e:
                    # 진짜 예외 상황.. 
                    continue
        try:
            sa_text_titles = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.link_column")))
        except TimeoutException:
            raise TimeoutException
        else:
            self.content_urls = [content_link.get_attribute("href")
                                 for content_link in sa_text_titles # 5개씩 수집하기 위해 임시로 슬라이싱 걸어놓음
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
    
def main(site_name:str) -> tuple[str]:
    if site_name not in ["naver", "daum"]:
        return None
    print(f"{site_name}_media_company.csv")
    
    media_company_table = pd.read_csv(f"{site_name}_media_company.csv")
    media_company = [x.strip() for x in media_company_table["media_company"].tolist()]
    
    data_dir = os.getenv("DATA_DIR")
    site_dir = os.path.join(data_dir, site_name)
    data = os.listdir(site_dir)
    
    remaining_items = list(set(data) ^ set(media_company))
    args = media_company_table[media_company_table["media_company"].isin(remaining_items)]
    codes = [os.path.basename(url) for url in args["url"].tolist()]
    codes = ['133710','268','259','251','305','162','314']
    print(len(remaining_items))
    quit()
    NewsCrawler(
        site_name=site_name,
        media_company_codes=codes,
        section_codes=("101"),
        scroll_range=10
    )
    
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # main("daum")
    # quit()
    # base_dir = r"C:\Users\HAMA\code\workspace\Storage\news\Data\naver"
    # folders = [os.path.join(base_dir, x) for x in os.listdir(base_dir)]
    # for folder in folders:
    #     if len(os.listdir(folder)) < 5:
            
            # media_company_table = pd.read_csv(f"daum_media_company.csv")