import sqlite3
import dryscrape
import urllib
from bs4 import BeautifulSoup

class Crawler:
    def __init__(self, p_from=0, p_to=10000):
        self.__session = dryscrape.Session()
        self.__main = "http://auto.ria.com"
        self.db = sqlite3.connect('cars.db',timeout=1).cursor()
        try:
            self.db.execute('''CREATE TABLE cars (name test, price integer, currency text, url text)''')
        except:
            print "Couldn't create new table"

        params = {
            'target': 'search',
            'event': 'little',
            'category_id':1,
            'bodystyle[0]':3,
            'bodystyle[1]':4,
            'bodystyle[2]':6,
            'chooseTypeSearchAuto':'oldAutos',
            'marka':58,
            'model':0,
            'state':0,
            's_yers':2004,
            'po_yers':0,
            'price_ot':p_from,
            'price_do':p_to,
            'currency':1
        }

        self.__params = urllib.urlencode(params)
    
    def get_cars(self, pages=None):
        self.__pages = pages
        self.__extract()
        self.sort()
        return self.cars()
    
    def cars(self):
        return [car for car in self.db.execute('select * from cars')]

    def __fetch(self, url):
        self.__session.visit(url)
        response = self.__session.body()
        if hasattr(self, 'soup'):
            self.soup.decompose()
        self.soup = BeautifulSoup(response)
        self.items = self.soup.find_all(class_= "content-bar")
        return

    def __extract(self):
        self.page = 0
        self.url = self.__main + "/search/?" + self.__params
        self.__fetch(self.url)

        print "first start"
        self.__crawl()
        return

    def __crawl(self):
        print "running algorithm. page: " + str(self.page)
        for item in self.items:
            head = item.find(class_="head-car").a
            name = head.text.strip()

            self.__span = item.find(class_="price").span
            self.__price = 0
            self.__currency = 'NONE'

            if self.__span:
                self.__price = int(''.join([s for s in self.__span.text if s.isdigit()]))
                self.__currency = self.__span.attrs['title']

            car = (name, self.__price, self.__currency, self.__main + head.attrs['href'])
            if name and self.__price: self.db.execute('INSERT INTO cars VALUES (?,?,?,?)', car,)

        self.page += 1
        url = self.url + '&page=' + str(self.page)
        self.__fetch(url)
        if self.__pages == None or self.__pages >= self.page: self.__crawl()

        return
