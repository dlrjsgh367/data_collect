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

class NewsCrawler:
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
                 site_name: str,  # 크롤링할 사이트 (네이버 또는 다음)
                 media_company_codes: tuple[str],  # 크롤링할 언론사 코드 목록
                 section_codes: tuple[str],  # 크롤링할 섹션 코드 목록
                 scroll_range: int  # 수집할 페이지 수
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
            raise ValueError("사이트 이름은 'naver' 또는 'daum'이어야 합니다.")

    def crawl_naver_news(self):
        for media_company_code in self.media_company_codes:
            link_collect_target = f"https://media.naver.com/press/{media_company_code}?sid={','.join(self.section_codes)}"
            try:
                self.collect_news_links(link_collect_target)
            except TimeoutException:
                print("링크 수집 중 TimeoutException 발생")
                continue
            self.collect_news_content()

    def crawl_daum_news(self):
        for media_company_code in self.media_company_codes:
            link_collect_target = f"https://v.daum.net/channel/{media_company_code}/contents"
            try:
                self.collect_news_links(link_collect_target)
            except TimeoutException:
                print("링크 수집 중 TimeoutException 발생")
                continue
            self.collect_news_content()

    def collect_news_links(self, media_company_url: str):
        self.webdriver.get(media_company_url)
        collect_range = range(self.scroll_range * 3)
        with tqdm(collect_range) as pbar:
            pbar.set_description(f"뉴스 콘텐츠 링크 수집 중..{media_company_url}")
            for _ in pbar:
                try:
                    self.webdriver.execute_script("window.scrollBy(0, 1000);")
                except Exception as e:
                    # 진짜 예외 상황.. 
                    continue
        try:
            if self.site_name == "naver":
                sa_text_titles = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.press_edit_news_link")))
            elif self.site_name == "daum":
                sa_text_titles = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.link_column")))
        except TimeoutException:
            raise TimeoutException
        else:
            self.content_urls = [content_link.get_attribute("href") for content_link in sa_text_titles[:5]]
        time.sleep(3)

    def collect_news_content(self):
        for content_url in self.content_urls:
            self.webdriver.get(content_url)
            time.sleep(3)
            title_element_xpath = {
                "naver": '/html/body/div/div[2]/div/div[1]/div[1]/div[1]/div[2]/h2',
                "daum": '/html/body/div[1]/main/section/div/article/div[1]/h3'
            }
            article_element_xpath = {
                "naver": '/html/body/div/div[2]/div/div[1]/div[1]/div[2]/div[1]',
                "daum": '/html/body/div[1]/main/section/div/article/div[2]/div[2]'
            }
            date_element_xpath = {
                "naver": '/html/body/div/div[2]/div/div[1]/div[1]/div[1]/div[3]/div[1]/div[1]/span',
                "daum": '/html/body/div[1]/main/section/div/article/div[1]/div[1]/span[2]/span'
            }
            media_company_selector = {
                "naver": 'media_end_linked_more_point',
                "daum": 'kakaoServiceLogo'
            }

            title = self.wait.until(EC.presence_of_element_located((By.XPATH, title_element_xpath[self.site_name])))
            article = self.wait.until(EC.presence_of_element_located((By.XPATH, article_element_xpath[self.site_name])))
            date = self.wait.until(EC.presence_of_element_located((By.XPATH, date_element_xpath[self.site_name])))
            media_company = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, media_company_selector[self.site_name])))

            data = (media_company.text, title.text, date.get_attribute("data-date-time"), article.text)
            self.save_to_file(data)

    def save_to_file(self, data: list):
        columns = ["media_company", "title", "date", "article"]
        media_company, title, _, _ = data

        only_korean = re.compile("[^ㄱ-ㅎㅏ-ㅣ가-힣]+")
        title = re.sub(only_korean, "", title)
        file_name = f'{self.site_name.upper()}_{title}_{media_company}.xlsx'
        download_path = os.path.join(self.DATA_DIR, self.site_name, media_company, file_name).replace('\\', '/')

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
    naver_media_company_codes = [os.path.basename(url) for url in naver_media_company["url"].to_list()]

    daum_media_company = pd.read_csv("daum_media_company.csv")
    daum_media_company_codes = [os.path.basename(url) for url in daum_media_company["url"].to_list()]

    nc = NewsCrawler(
        site_name='daum',
        media_company_codes=daum_media_company_codes,
        section_codes=("100",),  # 섹션 코드는 튜플 형태로 입력
        scroll_range=1
    )
