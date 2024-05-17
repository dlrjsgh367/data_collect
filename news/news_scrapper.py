import requests
import pandas as pd
from bs4 import BeautifulSoup

from interface import NewsScrapperInterface



class NewsScrapper(NewsScrapperInterface):
    def __init__(self):
        pass
    
    def send_request(self, url):
        return requests.get(url)

    def parse_content(self):
        pass
    
    def save_file(self):
        pass

def main(url_list, request_data_path=r"C:\data\Storage\news\Data\루시 Example.xlsx"):
    news_scrapper = NewsScrapper()
    
    if request_data_path == r"C:\data\Storage\news\Data\루시 Example.xlsx":
        request_data = pd.read_excel(request_data_path)
        request_data = request_data.dropna(axis=0, how='all')
        url_list = request_data.get("LINK")
    for url in url_list:
        res = news_scrapper.send_request(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        print(url)
        title = soup.find(id='title_area')
        body = soup.find(id='newsct_article')
        date = soup.select_one('.media_end_head_info_datestamp_time')
        press = soup.select_one('.media_end_head_top_logo_img.dark_type._LAZY_LOADING._LAZY_LOADING_INIT_HIDE')
        print(title)
        print(body)
        print(date)
        print(press)
        break
    

if __name__ == "__main__":
    main([], )
    pass