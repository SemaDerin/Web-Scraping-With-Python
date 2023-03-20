from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time
import pandas as pd
from selenium.webdriver.chrome.service import Service
from tqdm import tqdm


driver_path= "D:\DosyaYolu\chromedriver.exe"
service = Service(executable_path=driver_path)
browser = webdriver.Chrome(service=service)


class TrendyolScraper():
    def __init__(self):
        self.base_url= "https://www.trendyol.com/sr?q=bilgisayar&qt=bilgisayar&st=bilgisayar&os=1"
        self.pc_links= set()



    def get_categories(self):
        numbers= [2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50]
        result= list(map(lambda number: self.base_url+ "&pi={}".format(number), numbers))
        result.append("https://www.trendyol.com/sr?q=bilgisayar&qt=bilgisayar&st=bilgisayar&os=1")
        return result

    def get_source(self, url):
        browser.get(url)
        # Sayfa yüklenene kadar bekle
        while True:
            if browser.execute_script("return document.readyState") == "complete":
                break
            time.sleep(1)
        return BeautifulSoup(browser.page_source, "lxml")

    def get_pc_links(self,source):
        products = source.find_all("div", attrs={"class": "prdct-cntnr-wrppr"})
        for product in products:

            products_link = product.find_all("div", attrs={"class": "with-campaign-view"})
            for i in products_link:
                link = i.find("div", attrs={"class": "p-card-chldrn-cntnr"})
                link_start = "https://www.trendyol.com/"

                pc_links = list(map(lambda pc: link_start + pc.find("a").get("href"), products_link))
                return set(pc_links)

    def find_all_pc_links(self):
        categories = self.get_categories()
        bar = tqdm(categories, unit=" page link")
        for category_link in bar:
            bar.set_description(category_link)
            category_source = self.get_source(category_link)
            result = self.get_pc_links(category_source)
            self.pc_links = self.pc_links.union(result)

        return self.pc_links

    def get_name(self,source):
        try:
            return source.find("h1", attrs={"class": "pr-new-br"}).text
        except Exception:
            return None

    def get_teknik(self, source):
        try:
            table = source.find_all("ul", attrs={"class": "detail-attr-container"})
            attributes = {}
            for i in table:
                items = i.find_all("li", attrs={"class": "detail-attr-item"})
                for item in items:
                    teknik = item.find("span").text
                    deger = item.find("b").text
                    attributes[teknik] = deger
            return attributes
        except Exception:
            return None


    def scrape_pc(self):
        result = list()
        links = self.find_all_pc_links()
        bar = tqdm(links, unit="pc links")
        for link in bar:
            sections= list()
            bar.set_description(link)
            pc_source = self.get_source(link)
            marka=self.get_marka(pc_source)
            name = self.get_name(pc_source)
            price=self.get_price(pc_source)
            seller=self.get_seller(pc_source)
            seller_rate=self.get_seller_rate(pc_source)
            measure=self.get_measure(pc_source)
            measure_count=self.get_measure_count(pc_source)
            sorucevap=self.get_sorucevap_count(pc_source)
            attributes= self.get_teknik(pc_source)
            comment=self.get_product_reviews(pc_source)
            sections.append(attributes)


            result.append(dict(
                name=name,
                url=link,
                marka=marka,
                price=price,
                seller=seller,
                seller_rate=seller_rate,
                measure=measure,
                measure_count=measure_count,
                sorucevap=sorucevap,
                comment=comment,
                sections=sections



            ))
        return result


    def get_price(self,source):
        try:
            return source.find("span", attrs={"class": "prc-dsc"}).text
        except Exception:
            return None

    def get_seller(self, source):
        try:
            seller = source.find("div", attrs={"class": "seller-container"}).find("div", attrs={"class": "seller-name-text"}).text
            return seller


        except Exception:
            return "Trendyol"




    def get_measure(self,source):
        try:
            return source.find("div", attrs={"class": "category-rank-info"}).text
        except Exception:
            return  "-"

    def get_measure_count(self,source):

        try:

            measure_count = source.find("a", attrs={"class": "rvw-cnt-tx"}).text
        except:
            measure_count = "-"

        return measure_count

    def get_sorucevap_count(self,source):
        try:
            return source.find("a",attrs={"class":"product-questions"}).text
        except Exception:
            return None




    def get_product_reviews(self,source):
        reviews = []
        review_items = source.find_all('div', {'class': 'rnr-com-tx'})
        for review_item in review_items:
            review = review_item.find('p').text.strip()
            reviews.append(review)

        return reviews

    def get_marka(self,source):
        try:
            return source.find("h1",attrs={"class":"pr-new-br"}).find("a").text
        except Exception:
            return None



    def get_seller_rate(self, source):
        try:
            return source.find("div",attrs={"class":"pr-rnr-sm"}).find("div",attrs={"class":"pr-rnr-sm-p"}).find("span").text
        except Exception:
            return None

    def write_as_json(self, data):
        df = pd.DataFrame(data)

        # Write DataFrame to Excel file
        df.to_excel('x.xlsx', index=False)



if __name__=='__main__':
    scraper = TrendyolScraper()
    #source = scraper.get_source("https://www.trendyol.com/sr?q=bilgisayar&qt=bilgisayar&st=bilgisayar&os=1")
    #print(scraper.get_pc_links(source))
    data = scraper.scrape_pc()
    # data = write_as_json().scrape_pc()
    scraper.write_as_json(data)







