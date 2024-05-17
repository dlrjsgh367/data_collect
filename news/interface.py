from abc import ABC, abstractmethod



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

class NewsScrapperInterface(ABC):
    @abstractmethod
    def send_request(self):
        pass
    
    @abstractmethod
    def parse_content(self):
        pass
    
    @abstractmethod
    def save_file(self):
        pass