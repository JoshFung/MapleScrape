import json
import sqlite3
from datetime import datetime

import pandas as pd
from celery import shared_task
from decouple import config
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from scraping.models import Product
from scraping.stores.best_buy import best_buy
from scraping.stores.canada_computers import canada_computers
from scraping.stores.newegg import newegg


# ------------------------------------------------------------------------
# # TODO: Temporary Service() while Chromedriverv103 is broken
# # service = Service(executable_path=ChromeDriverManager().install())
# service = Service(executable_path=r"/Users/joshfung/Documents/PyCharm/learning-web-scrape/chromedriver")
#
# chrome_options = Options()
# # TODO: Remove when switching off beta of Chrome and Chromedriver
# chrome_options.binary_location = "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"
# chrome_options.page_load_strategy = 'normal'
# driver = webdriver.Chrome(service=service, options=chrome_options)
# driver.get("https://www.newegg.ca/Desktop-Graphics-Cards/SubCategory/ID-48?Tid=7708&PageSize=96")
# # driver.get("https://www.newegg.ca/Desktop-Graphics-Cards/SubCategory/ID-48/Page-7?Tid=7708&PageSize=96")
# ------------------------------------------------------------------------


@shared_task
def scrape():
    # service = Service(executable_path=ChromeDriverManager().install())
    service = Service(executable_path=config('CHROMEDRIVER_PATH'))

    chrome_options = Options()
    # TODO: Remove when switching off beta of Chrome and Chromedriver
    chrome_options.binary_location = "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"
    chrome_options.page_load_strategy = 'normal'
    # chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    conn = create_connection('db.sqlite3')
    with conn:
        delete_all_rows(conn)

    item_list = []

    driver.get(config('CANADA_COMPUTERS_URL'))
    canada_computers(driver, item_list)
    driver.get(config('BEST_BUY_URL'))
    best_buy(driver, item_list)
    driver.get(config('NEWEGG_URL'))
    newegg(driver, item_list)

    df = pd.DataFrame(item_list,
                      columns=['store', 'item', 'brand', 'normal_price', 'sale_price', 'rating', 'number_of_ratings',
                               'shipping', 'promo',
                               'out_of_stock'])

    file_name = fr'scraping/data/out-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
    df.to_json(file_name)
    save_function(file_name, len(item_list))

    driver.close()
    driver.quit()


@shared_task()
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Exception as e:
        print(e)
    return conn


@shared_task()
def delete_all_rows(conn):
    sql = 'DELETE FROM scraping_product'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


@shared_task(serializer='json')
def save_function(product_list: str, count: int):
    print('Starting save function')

    file = open(product_list)
    data = json.load(file)

    for item in range(count):
        Product.objects.create(
            store=data["store"][str(item)],
            name=data["item"][str(item)],
            brand=data["brand"][str(item)],
            normal_price=data["normal_price"][str(item)],
            sale_price=data["sale_price"][str(item)],
            rating=data["rating"][str(item)],
            num_of_ratings=data["number_of_ratings"][str(item)],
            shipping=data["shipping"][str(item)],
            promotion=data["promo"][str(item)],
            out_of_stock=data["out_of_stock"][str(item)],
        )

    file.close()
    print('Finished saving')
