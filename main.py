from crawler import DataCrawler
from db import db
import json
from analysis import ta
from datetime import datetime, date, timedelta


def load_stock_list(exchange):
    with open('./crawler/stock_list.json') as json_file:
        data = json.load(json_file)
        return data[str.lower(exchange)]


def save_stock_list():
    exchange = 'HNX'
    stock_list = load_stock_list(exchange)
    stock_list_tuple = [(stock, exchange) for stock in sorted(stock_list)]
    db.save_stock_list(stock_list_tuple)


def crawl(exchange=None, start_date=date.today().strftime("%d/%m/%Y"), end_date=date.today().strftime("%d/%m/%Y")):
    for (stock, exchange) in db.get_stock_symbol(exchange):
        crawler = DataCrawler.DataCrawler(stock, start_date=start_date, end_date=end_date)
        data = crawler.crawl()
        if data is not None:
            db.insert_stock_price(data)
            print('done crawl', exchange, ':', stock, 'from:', start_date, 'to:', end_date)
        else:
            print('ERROR crawl', exchange, ':', stock, 'from:', start_date, 'to:', end_date)


def crawl_one_stock():
    crawler = DataCrawler.DataCrawler('VCB', start_date='11/06/2020', end_date='12/06/2020')
    data = crawler.crawl()
    if data is not None:
        db.insert_stock_price(data)
    print(data)


def run_daily_crawl():
    # crawl()
    screen_date = '15/07/2020'
    bounce_watch_list, bounce_enter_list, ip_watch_list = ta.screener(screen_date)
    print('Bounce WATCHING list |', screen_date, bounce_watch_list)
    print('Impulse pullback WATCHING list |', screen_date, ip_watch_list)
    print('Bounce ENTER list |', screen_date, bounce_enter_list)


if __name__ == '__main__':
    run_daily_crawl()
