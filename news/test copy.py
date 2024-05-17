import requests
import pandas as pd
from bs4 import BeautifulSoup

class NewsScrapper:
    '''
    뉴스 스크래퍼
    '''
    def __init__(self, parse_script_dict):
        '''
        '''
        self.parse_script_dict = parse_script_dict

    def scrape_news(self, link):
        res = self.send_request(link)
        if not res:
            return None
        html = self.string_to_html(res)
        parse_result = self.parse_content(html, link)
        return parse_result

    def send_request(self, link):
        try:
            res = requests.get(link)
            res.raise_for_status()
            return res
        except requests.RequestException as e:
            print(f"요청을 보내는 중 오류가 발생했습니다: {e}")
            return None

    def string_to_html(self, res):
        return BeautifulSoup(res.text, 'html.parser')

    def parse_content(self, soup, link):
        main_link = "/".join(link.split("/")[:3]).replace('http', 'https').replace('httpss', 'https')
        parse_script = self.parse_script_dict.get(main_link)
        if not parse_script:
            print(f"파싱 스크립트를 찾을 수 없습니다. {main_link}")
            return None
        title = self._evaluate_script(soup, parse_script.get("title"))
        body = self._evaluate_script(soup, parse_script.get("body"))
        date = self._evaluate_script(soup, parse_script.get("date"))
        press = self._evaluate_script(soup, parse_script.get("press"))
        # return title, body, date, press
        return (bool(x) for x in (title,body,date,press))

    def _evaluate_script(self, soup, script):
        if not script:
            return None
        try:
            result = eval(script)
            print(result)
            return result.strip() if result else None
        except Exception as e:
            print(f"스크립트 evaluating 오류: {e}")
            return None

def main():
    parse_script_dict = {
        "https://news.naver.com": {
            "site_name": "네이버뉴스",
            "title": "soup.find(id='title_area').text",
            "body": "soup.find(id='newsct_article').text",
            "date": "soup.select_one('.media_end_head_info_datestamp_time').get('data-date-time')",
            "press": "soup.select_one('.media_end_head_top_logo_img.dark_type._LAZY_LOADING._LAZY_LOADING_INIT_HIDE').get('title')"
        },
        "https://v.daum.net": {
            "site_name": "다음뉴스",
            "title": "soup.find(class_='tit_view').text",
            "body": "soup.find(class_='article_view').text",
            "date": "soup.select_one('.num_date').text",
            "press": "soup.find(id='kakaoServiceLogo').text"
        },
        "https://news.nate.com": {
            "site_name": "네이트뉴스",
            "title": "soup.find(class_='articleSubecjt').text",
            "body": "soup.find(id='articleContetns').text",
            "date": "soup.find(class_='articleInfo').find(class_='medium').text",
            "press": "soup.find(class_='articleInfo').find(class_='firstDate').find('em').text"
        },
        "https://www.fntimes.com": {
            "site_name": "FNTIMES_한국금융신문",
            "title": "soup.find('h1').text",
            "body": "soup.find(class_='vcon_con_intxt').text",
            "date": "soup.find(class_='vcon_hd_din3').text.replace('기사입력 : ', '')",
            "press": "soup.find(class_='articleInfo').find(class_='firstDate').find('em').text" # 
        },
        "https://news.zum.com": {
            "site_name": "뉴스줌",
            "title": "soup.find(id='news_title').text",
            "body": "soup.find(id='article_body').text",
            "date": "soup.find(class_='article_info').find(class_='time').find('dd').text", 
            "press": "soup.find(class_='article_info').find(class_='media').text"
        },
        "https://opinion.inews24.com": {
            "site_name": "아이뉴스_오피니언",
            "title": "soup.find('h1').text",
            "body": "soup.find(id='articleBody').text",
            "date": "soup.find(class_='view').find('span').find('time').text",
            "press": "soup.find(class_='article_info').find(class_='media').text" # 
        },
        "https://www.inews24.com": {
            "site_name": "아이뉴스24",
            "title": "soup.find('h1').text",
            "body": "soup.find(id='articleBody').text",
            "date": "soup.find(class_='view').find('span').find('time').text",
            "press": "soup.find(class_='article_info').find(class_='media').text" # 
        },
        "https://www.pinpointnews.co.kr": {
            "site_name": "핀포인트뉴스",
            "title": "soup.find(class_='heading').text",
            "body": "soup.find(id='article-view-content-div').text",
            "date": "soup.find(class_='info-group').find(class_='item').find_all('li')[1].text.replace(' 입력 ', '')",
            "press": "soup.find(class_='article_info').find(class_='media').text" # 
        },
        "https://www.joongboo.com": {
            "site_name": "중부일보",
            "title": "soup.find(class_='heading').text",
            "body": "soup.find(id='article-view-content-div').text",
            "date": "soup.find(class_='info-group').find(class_='item').find_all('li')[1].text.replace(' 입력 ', '')",
            "press": "soup.find(class_='article_info').find(class_='media').text"
        },
        "https://www.mhns.co.kr": {
            "site_name": "중부일보",
            "title": "soup.find(class_='heading').text",
            "body": "soup.find(id='article-view-content-div').text",
            "date": "soup.find(class_='info-group').find(class_='item').find_all('li')[1].text.replace(' 입력 ', '')",
            "press": "soup.find(class_='article_info').find(class_='media').text"
        },
        "https://www.mhns.co.kr": {
            "site_name": "문화뉴스",
            "title": "soup.find(class_='heading').text",
            "body": "soup.find(id='article-view-content-div').text",
            "date": "soup.find(class_='info-group').find(class_='item').find_all('li')[1].text.replace(' 입력 ', '')",
            "press": "soup.find(class_='article_info').find(class_='media').text"
        },
        "https://www.srtimes.kr": {
            "site_name": "SR타임스",
            "title": "soup.find(class_='heading').text",
            "body": "soup.find(id='article-view-content-div').text",
            "date": "soup.find(class_='info-group').find(class_='item').find_all('li')[1].text.replace(' 입력 ', '')",
            "press": "soup.find(class_='article_info').find(class_='media').text"
        },
        # "https://www.mbnmoney.mbn.co.kr": {
        #     "site_name": "매일경제",
        #     "title": "soup.find(class_='newsview_title').text",
        #     "body": "soup.find(id='news_contents').text",
        #     "date": "soup.find(class_='newsview_box').find(class_='date')",
        #     "press": "soup.find(class_='article_info').find(class_='media').text"
        # },
        
        
    }

    ns = NewsScrapper(parse_script_dict)
    parse_result = ns.scrape_news('https://www.thebestnews.kr/news/articleView.html?idxno=282461')
    if parse_result:
        print(list(parse_result))
        pass

if __name__ == '__main__':
    main()
    global l
    l = [
        'https://n.news.naver.com/mnews/article/031/0000816889?rc=N&ntype=RANKING&sid=001'
        'https://v.daum.net/v/20240301000029657',
        'https://news.nate.com/view/20240301n00021?mid=n0100',
        'https://www.fntimes.com/html/view.php?ud=202402292347175433c1c16452b0_18',
        'http://news.zum.com/articles/89082515',
        'https://opinion.inews24.com/view/1692184',
        'https://www.inews24.com/view/1692184',
        'https://www.pinpointnews.co.kr/news/articleView.html?idxno=249116',
        'http://www.joongboo.com/news/articleView.html?idxno=363637337',
        'http://www.mhns.co.kr/news/articleView.html?idxno=575429',
        'https://www.srtimes.kr/news/articleView.html?idxno=152367',
        
        'http://mbnmoney.mbn.co.kr/news/view?news_no=MM1005161262',
        
        'https://www.thebestnews.kr/news/articleView.html?idxno=282461',
        
        'https://www.webeconomy.co.kr/news/article.html?no=866261',
        'http://www.mdtimes.kr/617426',
        'https://www.chosun.com/culture-life/culture_general/2024/03/01/SCQDWEFY2FFK7LSQENG4T3JRDI/',
        'https://www.kmib.co.kr/article/view.asp?arcid=1709188364&code=11171399&sid1=all',
        'https://www.asiae.co.kr/article/2024022916513306615',
        'https://www.hankyung.com/article/202403010770Y',
        'https://sports.news.naver.com/golf/news/read.nhn?oid=277&aid=0005386660',
        'https://www.yna.co.kr/view/AKR20240229151100063',
        'https://www.wowtv.co.kr/NewsCenter/News/Read?articleId=A202403010011',
        'https://biz.chosun.com/topics/law_firm/2024/03/01/IISKCC3GJ5H3NGMZR442VG5U6Y/',
        'https://www.mk.co.kr/news/society/10954421',
        'https://m.newspic.kr/view.html?nid=2024030106000350877&pn=214',
        'https://www.goodmorningcc.com/news/articleView.html?idxno=307025',
        'http://www.gunchinews.com/news/articleView.html?idxno=66224',
        'http://www.ohnews.co.kr/news/articleView.html?idxno=23101',
        'http://www.tvj.co.kr/news/articleView.html?idxno=93952'
    ]