import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from naver_news_crawler import NaverNewsCrawler
from daum_news_crawler import DaumNewsCrawler

def main():
    press_dataframe = pd.read_csv(r"C:\data\Storage\news\daum_media_company.csv")
    press_link_list = press_dataframe["url"].tolist()
    press_name_list = press_dataframe["media_company"].tolist()
    press_link_list = ["https://v.daum.net/channel/8"]
    DaumNewsCrawler(
        chrome_version = "124.0.6367.119",
        scroll_range=20,
        press_link_list = press_link_list,
        press_name_list = press_name_list,
    )

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_env = load_dotenv()
    print(load_env)
    main()