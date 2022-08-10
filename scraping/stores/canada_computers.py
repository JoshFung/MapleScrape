import re
from time import sleep

from bs4 import BeautifulSoup
from celery import shared_task


@shared_task
def canada_computers(driver, item_list):
    load_all(driver)

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    get_all_items(soup, item_list)


@shared_task
def get_all_items(soup, entries):
    item_grid = soup.find('div', {'id': 'product-list'})
    all_items = item_grid.find_all('div', {'class': 'productTemplate'})

    item_num = 1

    for item in all_items:
        item_entry = item_details(item)
        entries.append(item_entry)
        print(f'CANADA COMPUTERS ITEM #:{item_num}')
        item_num += 1


@shared_task
def get_name_and_brand(item, entry):
    parent_element = item.find('span', {'class': 'productTemplate_title'})
    item_name = parent_element.find('a', recursive=False).get_text()
    name_and_brand = item_name.split(' ', 1)
    entry.update({'item': name_and_brand[1]})
    entry.update({'brand': name_and_brand[0]})


@shared_task
def extract_num(string):
    no_commas = string.replace(",", "")
    filtered_string = re.findall(r'\d+\.\d+', no_commas)[0]

    return filtered_string


@shared_task
def get_price(item, entry):
    item_name = item.find('span', {'class': 'productTemplate_title'})
    current_price_element = item.find('span', {'class': 'pq-hdr-product_price'})
    current_price = extract_num(current_price_element.get_text())

    # there is a sale
    if current_price_element.find_previous_sibling("span") != item_name:
        # print('sale')
        previous_price = current_price_element.find_previous_sibling('span').get_text()
        previous_price = extract_num(previous_price)
        entry.update({'normal_price': previous_price})
        entry.update({'sale_price': current_price})

    # there is no sale
    else:
        previous_price = None
        entry.update({'normal_price': current_price})
        entry.update({'sale_price': previous_price})


@shared_task
def get_rating(entry):
    # canada computers has no rating system
    entry.update({'rating': None})
    entry.update({'number_of_ratings': None})


@shared_task
def get_shipping(item, entry):
    entry.update({'shipping': None})

    item_shipping_parent = item.find('div', {'class': 'text-danger'})

    if item_shipping_parent is not None and item_shipping_parent.find('small') is not None:
        print(item_shipping_parent.find('small').get_text())
        entry.update({'shipping': 'Free Shipping'})


@shared_task
def get_availability(item, entry):
    availability_element = item.find('small', {'class': 'pq-hdr-bolder'})
    str_availability_element = str(availability_element)
    pattern = r'\bAvailable to Ship\b'
    if re.search(pattern, str_availability_element) is not None:
        entry.update({'out_of_stock': 'False'})
        print('in stock')
    else:
        entry.update({'out_of_stock': 'True'})
        print('out of stock')


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
    item_entry.update({'store': 'Canada Computers'})
    get_name_and_brand(item, item_entry)
    get_price(item, item_entry)
    get_rating(item_entry)
    get_shipping(item, item_entry)
    get_availability(item, item_entry)
    return item_entry


@shared_task
def load_all(driver):
    scroll_count = 30

    for i in range(1, scroll_count):
        driver.execute_script("window.scrollTo(1, 50000)")
        sleep(3)
