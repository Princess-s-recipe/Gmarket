import scrapy
from fisa.items import FisaItem 
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from time import sleep

class ExampleSpider(scrapy.Spider):
    name = "fisa_spider"
    start_urls = ['https://browse.gmarket.co.kr/search?keyword=%EB%A7%A5%EB%B6%81&t=s&k=0&p=1']

    # 먼저, 셀레니움을 활용하여 웹브라우저 제어하기
    def start_requests(self):
        chrome_driver_path = "E:/jupyter notebook/3.crawling/chromedriver.exe"
        self.driver = webdriver.Chrome(chrome_driver_path)
        self.driver.get(self.start_urls[0])

        # 스크롤이 더 이상 내려가지 않을 때까지 반복
        while True:
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            # 스크롤을 끝까지 내림
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(4) 

            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

        yield scrapy.Request(self.driver.current_url, callback=self.parse, dont_filter=True, meta={'driver': self.driver})
            
    # 받아온 웹페이지 소스에서 원하는 데이터 파싱하기
    def parse(self, response):
        driver = response.meta['driver']
        response = scrapy.http.HtmlResponse(driver.current_url, body=driver.page_source, encoding='utf-8')        
        products = response.css('#section__inner-content-body-container > div > div > div.box__item-container > div.box__information') 
        
        for product in products:
            example_item = FisaItem()
            example_item['name'] = product.css('div.box__information > div.box__information-major > div.box__item-title > span > a > span.text__item::text').get()
            example_item['price'] = product.css('div.box__information > div.box__information-major > div.box__item-price > div.box__price-seller > strong::text').get()
            example_item['unit'] = product.css('div.box__information > div.box__information-major > div.box__item-price > div.box__price-seller > span.text.text__unit::text').get()
            yield example_item 
