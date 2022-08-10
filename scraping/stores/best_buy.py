import re
from time import sleep

from bs4 import BeautifulSoup
from celery import shared_task
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By


@shared_task
def best_buy(driver, item_list):
    code = load_all(driver)
    print(f'CODE: {code}')

    # if we site failed to load
    if code == 400 or code == 404:
        return

    sleep(5)

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
    except IndexError as e:
        entry.update({'brand': None})
        entry.update({'item': name_and_brand[0]})


@shared_task
def extract_num(string):
    print(f'NUM: {string}')
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
    print(f'RATING: {item_rating} => # of RATINGS: {num_ratings}')
    entry.update({'rating': item_rating})
    entry.update({'number_of_ratings': num_ratings})


@shared_task
def get_shipping(item, entry):
    item_shipping = item.find('span', {'class': 'container_1DAvI'}).get_text()
    item_shipping = item_shipping.strip()
    if item_shipping != 'Available to ship':
        item_shipping = 'Sold out online'
    entry.update({'shipping': item_shipping})


@shared_task
def get_availability(item, entry):
    availability = item.find('span', {'class': 'container_1DAvI'}).get_text()
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
    failure_count = 0

    while True:
        sleep(3)
        driver.execute_script("window.scrollTo(1,50000)")
        try:
            driver.find_element(By.CLASS_NAME, 'endOfList_b04RG')
            return 200
        except (NoSuchElementException, ElementNotInteractableException) as e:
            try:

                button = driver.find_element(By.XPATH,
                                             '/html/body/div[1]/div/div[2]/div[1]/div/main/a/div/button')
                driver.execute_script('arguments[0].click();', button)
            except (NoSuchElementException, ElementNotInteractableException) as e:
                print('COULD NOT FIND LOAD MORE NOR END OF LIST')
                failure_count += 1
                if failure_count == 30:
                    return 404
