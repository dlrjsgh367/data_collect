import requests
import pandas as pd
from bs4 import BeautifulSoup

from interface import NewsScrapperInterface



class NewsScrapper(NewsScrapperInterface):
    '''
    뉴스 스크래퍼
    '''
    def __init__(self, press_name_select_dict, bs4_parse_script_dict):
        self.press_name_select_dict = press_name_select_dict
        self.bpsd = bs4_parse_script_dict.get("data")
        
        # self.press_name = None
        # self.res = None
        # self.soup = None
        # self.res = None
        # self.parse_result = (None, None, None, None)
        
        # self.send_request()
        # self.parse_content()
        
    def send_request(self, link):
        main_link = "/".join(link.split("/")[:3])
        press_name = self.press_name_select_dict.get(main_link)
        self.press_name = press_name

        res = requests.get(link)
        return res
        # self.res = res
        
    def string_to_html(self, res):
        soup = BeautifulSoup(res.text, 'html.parser')
        # self.soup = soup
        return soup
    
    def parse_content(self, soup):
        title = eval(self.bpsd[self.press_name].get("title"))
        body = eval(self.bpsd[self.press_name].get("body"))
        date = eval(self.bpsd[self.press_name].get("date"))
        press = eval(self.bpsd[self.press_name].get("press"))
        
        parse_result = (title, body, date, press)
        return parse_result
        # self.parse_result = parse_result
        
    def save_file(self):
        pass

def main():
    request_data_path = r"C:\data\Storage\news\Data\루시 Example.xlsx"
    request_data = pd.read_excel(request_data_path)
    request_data = request_data.dropna(axis=0, how='all')
    test = request_data.copy()
    test = test.drop(['문서번호', '수집번호', '채널', '수집일', '수집월', '작성자 ID', '작성자 NICK', '제목', '수집원', '루시 감성', '주제', '전체 연관어', '태그'], axis=1)
    site_dict = {site: '/'.join(link.split('/')[:3]) for (site, link) in zip(test.get("사이트").tolist(), test.get("LINK").tolist())}
    reverse_site_dict = dict((v,k) for k,v in site_dict.items())
    
    bs4_parse_script_dict = {
        "data": {
            "네이버뉴스": {
                "title": "soup.find(id='title_area').text",
                "body": "soup.find(id='newsct_article').text",
                "date": "soup.select_one('.media_end_head_info_datestamp_time').get('data-date-time')",
                "press": "soup.select_one('.media_end_head_top_logo_img.dark_type._LAZY_LOADING._LAZY_LOADING_INIT_HIDE').get('title')"
            },
            "다음뉴스": {
                "title": "soup.find(class_='tit_view')",
                "body": "soup.find(class_='article_view').text",
                "date": "soup.select_one('.num_date').text",
                "press": "soup.find(id='kakaoServiceLogo').text"
            },
            "네이트뉴스": {
                "title": "soup.find(id='title_area').text",
                "body": "soup.find(id='newsct_article').text",
                "date": "soup.select_one('.media_end_head_info_datestamp_time').get('data-date-time')",
                "press": "soup.select_one('.media_end_head_top_logo_img.dark_type._LAZY_LOADING._LAZY_LOADING_INIT_HIDE').get('title')"
            },
            
        }
    }
    ns = NewsScrapper(reverse_site_dict, bs4_parse_script_dict)
    res = ns.send_request("https://v.daum.net/v/20240301000029657")
    html = ns.string_to_html(res)
    parse_result = ns.parse_content(html)
    print(parse_result)

if __name__ == '__main__':
    main()