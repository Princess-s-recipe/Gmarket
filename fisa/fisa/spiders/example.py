import scrapy
from utills.items import FisaItem 
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from time import sleep

class ExampleSpider(scrapy.Spider):
    name = "fisa_spider"
    start_urls = ['https://search.shopping.naver.com/search/all?query=%EB%A7%A5%EB%B6%81&bt=2&frm=NVSCPRO']

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
        products = response.css('#content > div.style_content__xWg5l > div.basicList_list_basis__uNBZx > div > div') 
        
        # 광고성 상품이냐, 일반 상품이냐에 따라 사용하는 CSS주소가 다름
        for product in products:
            is_ad_product = bool(product.css('div.adProduct_info_area__dTSZf'))
            example_item = FisaItem()

            if is_ad_product:
                example_item['name'] = product.css('div.adProduct_title__amInq > a::text').get()
                example_item['price'] = product.css('div.adProduct_price_area__yA7Ad > strong > span.price_price__LEGN7 > span::text').get()
            else:
                example_item['name'] = product.css('div.product_title__Mmw2K > a::text').get()
                example_item['price'] = product.css('div.product_price_area__eTg7I > strong > span.price_price__LEGN7 > span.price_num__S2p_v::text').get()

            yield example_item 
