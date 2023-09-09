from random import randint
import re
from time import sleep

from bs4 import BeautifulSoup
from celery import shared_task
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@shared_task
def best_buy(driver, item_list):
    status_code = load_all(driver)
    print(f'CODE: {status_code}')

    # if we site failed to load
    if status_code == 400 or status_code == 404:
        return

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    get_all_items(soup, item_list)


@shared_task
def get_all_items(soup, entries):
    item_grid = soup.find('div', {'class': 'productsRow_DcaXn row_1mOdd'})
    all_items = item_grid.find_all('a', {'itemprop': 'url'})

    item_num = 1

    for item in all_items:
        item_entry = item_details(item)
        entries.append(item_entry)
        print(f'BEST BUY ITEM #:{item_num}')
        item_num += 1


@shared_task
def get_name_and_brand(item, entry):
    item_name = item.find('div', {'itemprop': 'name'}).get_text()

    name_and_brand = item_name.split(' ', 1)
    try:
        entry.update({'item': name_and_brand[1]})
        entry.update({'brand': name_and_brand[0]})
        print(f'ITEM NAME: {name_and_brand[1]}')
    except IndexError as e:
        entry.update({'brand': None})
        entry.update({'item': name_and_brand[0]})
        print(f'ITEM NAME: {name_and_brand[0]}')


@shared_task
def extract_num(string):
    # print(f'NUM: {string}')
    no_commas = string.replace(",", "")
    try:
        filtered_string = re.findall(r'\d+\.\d+', no_commas)[0]
    except IndexError:
        filtered_string = re.findall(r'\d+', no_commas)[0]

    return filtered_string


@shared_task
def get_price(item, entry):
    price = item.find('div', {'class': 'price_2j8lL'}).div.get_text()
    price = extract_num(price)

    discount = item.find('span', {'class': 'productSaving_3T6HS'})
    if discount is not None:
        discount = discount.get_text()
        discount = extract_num(discount)
        sale_price = price
        normal_price = float(price) + float(discount)
    else:
        normal_price = price
        sale_price = None

    entry.update({'normal_price': normal_price})
    entry.update({'sale_price': sale_price})


@shared_task
def get_rating(item, entry):
    item_rating = item.find('meta', {'itemprop': 'ratingValue'})['content']
    num_ratings = item.find('meta', {'itemprop': 'reviewCount'})['content']
    # print(f'RATING: {item_rating} => # of RATINGS: {num_ratings}')
    entry.update({'rating': item_rating})
    entry.update({'number_of_ratings': num_ratings})


@shared_task
def get_shipping(item, entry):

    element = item.find('span', {'class': 'container_1DAvI'})
    if element is None:
        entry.update({'shipping': ''})
        print('NUM COULDN\'T FIND SHIPPING CLASS')
        return
    element_text = element.get_text()
    item_shipping = element_text.strip()
    if item_shipping != 'Available to ship':
        item_shipping = 'Sold out online'
    entry.update({'shipping': item_shipping})


@shared_task
def get_availability(item, entry):
    element = item.find('span', {'class': 'container_1DAvI'})
    if element is None:
        entry.update({'out_of_stock': 'False'})
        return
    availability = element.get_text()
    if availability == "Available to ship":
        entry.update({'out_of_stock': 'False'})
    else:
        entry.update({'out_of_stock': 'True'})


# @shared_task()
# def get_item_id(item, entry):
#     item_strong_tag = item.find('strong', string='Item #: ')
#     if item_strong_tag is None:
#         item_strong_tag = item.find('strong', string='Model #: ')
#
#     if item_strong_tag is None:
#         entry.update({'item_id': None})
#     else:
#         item_text = item_strong_tag.parent.text
#         pattern = re.compile('\\b(Item #: |Model #: )')
#         item_id = re.sub(pattern, '', item_text)
#         entry.update({'item_id': item_id})


@shared_task
def item_details(item):
    item_entry = {}
    item_entry.update({'store': 'Best Buy'})
    get_name_and_brand(item, item_entry)
    get_price(item, item_entry)
    get_rating(item, item_entry)
    get_shipping(item, item_entry)
    get_availability(item, item_entry)
    return item_entry


@shared_task
def load_all(driver):
    print("Starting load_all")

    while True:
        print("Scrolling down")
        driver.execute_script("window.scrollBy(1,1500)")
        try:
            print("Waiting to find show more button...")
            WebDriverWait(driver, 15).until(EC.any_of(
                EC.element_to_be_clickable((By.CLASS_NAME, 'loadMore_3AoXT')),
                EC.presence_of_element_located((By.CLASS_NAME, 'endOfList_b04RG'))
            ))
            
            element = driver.find_element(By.CLASS_NAME, 'loadMore_3AoXT')
            print("Click show more button...")
            element.click()

            
        except NoSuchElementException:
            # driver.execute_script("window.scrollBy(1,1500)")
            print("No more load more elements found")
            return 200

        except TimeoutException:
            print("TimeoutException when looking for pagination element or no more div")
            return 404

