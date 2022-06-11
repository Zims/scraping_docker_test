# save this as app.py
from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
# from classes import Database, AdScraper

app = Flask(__name__)
import requests
from bs4 import BeautifulSoup
from lxml import etree
import time
from datetime import datetime
import sqlite3
import random


class AdScraper:
    def __init__(self, min_pages=10, mid_pages=20, max_pages=50):
        self.min_pages = min_pages
        self.mid_pages = mid_pages
        self.max_pages = max_pages
        self.url_collector = []
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
        ]
        self.detail_list = []

    def get_urls_from_site(self, page_range=range(1, 2)):
        for page_nr in page_range:
            response = requests.get(f'https://www.ss.lv/lv/real-estate/flats/riga/all/page{page_nr}.html')
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('form', id_='filter_frm')[0].select('table')[2].select('tr')
            for item in items:
                try:
                    extracted_url = f"https://www.ss.lv{item.select('a')[0].get('href')}"
                    self.url_collector.append(extracted_url)
                except:
                    continue
            print(f'Page {page_nr} collected')
            time.sleep(0.3)
        # print(self.url_collector)
        return self.url_collector


    def scrape_single_page(self, url_collector):
        print("Collecting details ...")

        for collected_url in url_collector:
            try:
                r = requests.get(
                    collected_url, headers={'User-Agent': random.choice(self.user_agents)})
                root = etree.HTML(r.text)
            except:
                print("Nepareiza saite")
                print(collected_url)
            # create a tree from the html string
            try:
                tx_type = root.xpath('//h2[@class="headtitle"]/text()')
                tx_type = tx_type[-1].replace(' / ', '')
            except:
                tx_type = 'N/A'

            try:
                description = root.xpath('//div[@id="msg_div_msg"]/text()')
                description = " ".join(description).strip().replace('\t', '').replace('\n', '').replace('\r', '')
            except:
                description = "N/A"
            try:
                city = root.xpath('//td[@id="tdo_20"]/b/text()')[0]
            except:
                city = None

            try:
                district = collected_url.split('/')[-2].replace('-', '_')
            except:
                district = None
            else:
                try:
                    district = district.lower()
                except:
                    district = district

            try:
                street = root.xpath('//td[@id="tdo_11"]/b/text()')[0]
            except:
                street = None
            try:
                rooms = root.xpath('//td[@id="tdo_1"]/text()')[0]
            except:
                rooms = None
            try:
                size = root.xpath('//td[@id="tdo_3"]/text()')[0].split(' ')[0]
            except:
                size = None
            try:
                floor = root.xpath('//td[@id="tdo_4"]/text()')[0].split('/')[0]
            except:
                floor = None
            try:
                max_floor = root.xpath('//td[@id="tdo_4"]/text()')[0].split('/')[1]
            except:
                max_floor = None
            try:
                series = root.xpath('//td[@id="tdo_6"]/text()')[0]
            except:
                series = None
            try:
                item_type = root.xpath('//td[@id="tdo_2"]/text()')[0]
            except:
                item_type = None
            try:
                extras = root.xpath('//td[@id="tdo_1734"]/text()')[0]
            except:
                extras = None
            try:
                price = root.xpath(
                    '//td[@id="tdo_8"]/text()')[0].split('€')[0].replace(' ', '')
            except:
                price = None
            try:
                date_added = root.xpath(
                    '//td[@valign="bottom"]/table/*/*/text()')[0].replace('Datums: ', '').split(' ')[0].strip()

                # convert date_added from %dd.%mm.%yyyy to %yyyy-%mm-%dd
                date_added = date_added.split('.')[2] + '-' + date_added.split('.')[1] + '-' + date_added.split('.')[0]
                date_added = date_added.strip()

            except:
                date_added = None

            detail_set = {
                'tx_type': tx_type,
                'description': description,
                'city': city,
                'district': district,
                'street': street,
                'rooms': rooms,
                'size': size,
                'floor': floor,
                'max_floor': max_floor,
                'series': series,
                'item_type': item_type,
                'extras': extras,
                'price': price,
                'date_added': date_added,
                'url': collected_url
            }
            self.detail_list.append(detail_set)


class Database:
    def __init__(self, detail_list=[]):
        self.detail_list = detail_list

        self.conn = sqlite3.connect('ss_all_with_class.sqlite3', check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute(
            '''CREATE TABLE IF NOT EXISTS ss_all_new (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                                    description TEXT,
                                                                    city TEXT,
                                                                    district TEXT,
                                                                    street TEXT,
                                                                    rooms INTEGER,
                                                                    size INTEGER,
                                                                    floor INTEGER,
                                                                    max_floor INTEGER,
                                                                    series TEXT,
                                                                    item_type TEXT,
                                                                    extras TEXT,
                                                                    price INTEGER,
                                                                    tx_type TEXT,
                                                                    date_added DATE,
                                                                    url TEXT,
                                                                    added_to_db TIMESTAMP
                                                                    )''')

    def remove_old_records(self):

        """
        remove old records from db older than 10 days
        """
        try:
            self.cur.execute('''DELETE FROM ss_all_new WHERE date_added < date('now','-10 days')''')
            self.conn.commit()
            # remove broken records from db younger then a day
            self.cur.execute('''DELETE FROM ss_all_new WHERE date_added > date('now','+1 days')''')
            self.conn.commit()
            # set time every day at 3 am
            night_time = datetime.now().strftime('%H:%M')
            if night_time == '03:00':
                self.cur.execute('''DELETE FROM ss_all_new WHERE date_added < date('now','-1 days')''')
                self.conn.commit()
        except:
            print('No records to delete')
        
    def add_new_records(self, detail_list):
        # get all urls in db
        self.cur.execute('''SELECT url FROM ss_all_new''')
        db_urls = self.cur.fetchall()

        # compare detail_list urls with db urls and add new records for urls that are not in db
        db_list = [db_url[0] for db_url in db_urls]


        for detail in detail_list:
            if detail['url'] not in db_list:
                date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.cur.execute('''INSERT INTO ss_all_new (description, city, district, street, rooms, size, floor, max_floor, series, item_type, extras, price, tx_type, date_added, url, added_to_db) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                                    (detail['description'],
                                    detail['city'],
                                    detail['district'],
                                    detail['street'],
                                    detail['rooms'],
                                    detail['size'],
                                    detail['floor'],
                                    detail['max_floor'],
                                    detail['series'],
                                    detail['item_type'],
                                    detail['extras'],
                                    detail['price'],
                                    detail['tx_type'],
                                    detail['date_added'],
                                    detail['url'],
                                    date_now))
                self.conn.commit()
                print('Record already in db')
        print("Adding new records...")

                # todays records count
        self.cur.execute('''SELECT COUNT(*) FROM ss_all_new WHERE date_added = date('now')''')
        todays_records = self.cur.fetchall()
        print('Todays records: ', todays_records[0][0])
# # Database connection
# conn = sqlite3.connect('ss_all_with_class.sqlite3', check_same_thread=False)
# c = conn.cursor()

# Endpoints #
@app.get("/")
async def index():
    return '<a href="/today">Todays listings</a>'
    
@app.get("/today")
async def today():
    todays_date = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT * FROM ss_all_new WHERE date_added = ? ORDER BY added_to_db DESC", (todays_date,))
    # put them in a list
    todays_ads = [dict(zip([key[0] for key in c.description], row)) for row in c.fetchall()]
    todays_ads = jsonify(todays_ads)
    # return todays_ads as json format
    return todays_ads
    
# @app.get("/update")
# async def update():
#     db = Database()
#     db.remove_old_records()
#     ad_scraper = AdScraper()
#     ad_scraper.scrape_single_page(ad_scraper.get_urls_from_site(range(0, 4)))
    
#     db.add_new_records(ad_scraper.detail_list)
#     # todays records count
#     db.cur.execute('''SELECT COUNT(*) FROM ss_all_new WHERE date_added = date('now')''')
#     todays_records = db.cur.fetchall()
#     today = todays_records[0][0]

#     return '<h1>Scraper is running...</h1>' + '<h2>Today\'s records: ' + str(today) + '</h2>' + '<a href="/today">Todays listings</a>'

    



# @app.get("/places")
# async def places(request: Request):
#     # return all places in database
#     # only unique values for rajons
#     c.execute("SELECT DISTINCT district FROM ss_all_new")
#     # put them in a list
#     district = [row[0] for row in c.fetchall()]
#     return district


# @app.get("/{district}/{end_date}")
# async def district(request: Request, district: str, end_date: str):
#     district = district.replace('_', ' ')
#     end_date = end_date.replace('_', '-')
#     c.execute("SELECT * FROM ss_all_new WHERE district = ? AND date_added >= ? ORDER BY added_to_db DESC", (district, end_date))
#     # put them in a list
#     district_ads = [dict(zip([key[0] for key in c.description], row)) for row in c.fetchall()]
#     return district_ads


# @app.get("/{place:str}")
# def get_place(place):
#     if place == "top100":
#         # select only top 100 newest records
#         c.execute("SELECT * FROM ss_all_new ORDER BY added_to_db DESC LIMIT 100")
#         top100 = [dict(zip([key[0] for key in c.description], row)) for row in c.fetchall()]
#         return top100
#     # elif place == "all":
#     #         # select entire_db newest records
#     #     c.execute("SELECT * FROM ss_all_new ORDER BY date_added DESC")
#     #     entire_db_resp = [dict(zip([key[0] for key in c.description], row)) for row in c.fetchall()]
#     #     return entire_db_resp
#     else:
#         c.execute("SELECT * FROM ss_all_new WHERE district = ? ORDER BY added_to_db DESC LIMIT 300", (place,))
#         place_appartments = [dict(zip([key[0] for key in c.description], row)) for row in c.fetchall()]
#         return place_appartments

if __name__ == "__main__":
    app.run(debug=True)
