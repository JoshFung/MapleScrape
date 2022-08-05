from time import sleep

from bs4 import BeautifulSoup
from celery import shared_task
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from urllib3.exceptions import MaxRetryError


@shared_task
def best_buy(driver, item_list):
    code = load_all(driver)
    print(f'CODE: {code}')

    # if we site failed to load
    if code == 400:
        return

    # # TODO: first delay
    sleep(5)

    print('FLAG 10')
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    get_all_items(soup, item_list)


@shared_task
def get_all_items(soup, entries):
    print('FLAG 11')
    all_items = soup.find_all('a', {'itemprop': 'url'})
    print(f'BEST BUY # OF ITEMS: {len(all_items)}')
    print('FLAG 12')

    for item in all_items:
        print(item)
        item_entry = item_details(item)
        entries.append(item_entry)


@shared_task
def get_name_and_brand(item, entry):
    print('FLAG 15')
    print('FLAG 16')
    item_name = item.find('div', {'itemprop': 'name'}).get_text()
    name_and_brand = item_name.split(' ', 1)
    entry.update({'brand': name_and_brand[0]})
    entry.update({'item': name_and_brand[1]})


@shared_task
def extract_num(string):
    print('FLAG 18')
    print(f'NUM: {string}')
    # no_commas = string.replace(",", "")
    # print(f'NO COMMAS NUM: {no_commas}')
    # filtered_string = re.findall(r"\d+\.\d+", no_commas)
    filtered_string = string.strip('SAVE $')
    print(f"FILTERED STRING: {filtered_string}")
    return filtered_string[0]


@shared_task
def get_price(item, entry):
    print('FLAG 17')
    price = item.find('div', {'class': 'price_2j8lL'}).div.get_text()
    price = extract_num(price)
    print('FLAG 19')

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
    item_rating = item.find('meta', {'itemprop': 'ratingValue'})
    num_ratings = item.find('meta', {'itemprop': 'reviewCount'})
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
    print('FLAG 13')
    item_entry.update({'store': 'Best Buy'})
    print('FLAG 14')
    get_name_and_brand(item, item_entry)
    get_price(item, item_entry)
    get_rating(item, item_entry)
    get_shipping(item, item_entry)
    get_availability(item, item_entry)
    return item_entry


@shared_task
def load_all(driver):
    scroll_num = 3
    for i in range(1, scroll_num):
        driver.execute_script("window.scrollTo(1,50000)")
        sleep(1)

    while True:
        try:
            print('FLAG 1')
            driver.find_element(By.CLASS_NAME, 'endOfList_b04RG')
            print('FLAG 2')
            return 200
        except (NoSuchElementException, ElementNotInteractableException) as e:
            try:
                print('FLAG 3')
                # WebDriverWait(driver, 25).until(
                #     EC.element_to_be_clickable((By.CLASS_NAME, 'button_E6SE9')))
                # driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/main/a/div/button').click()
                # driver.find_element(By.CLASS_NAME, 'button_E6SE9').click()

                # button = driver.find_element(By.CLASS_NAME, 'button_E6SE9')
                button = driver.find_element(By.XPATH,
                                             '/html/body/div[1]/div/div[2]/div[1]/div/main/a/div/button')
                driver.execute_script('arguments[0].click();', button)
                # driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/div/main/a/div/button').click()
            # except (NoSuchElementException, ElementNotInteractableException) as e:
            #     print('FLAG 4')
            #     return 404
            except (NoSuchElementException, ElementNotInteractableException) as e:
                print('FLAG 7')
                try:
                    # if driver.find_element(By.CLASS_NAME,
                    #                        'materialOverride_STCNx toolbarTitle_2lgWp').get_text() == '0 results':
                    # total_results = driver.find_element(By.XPATH,
                    #                                     '/html/body/div[1]/div/div[2]/div[1]/div/main/div[1]/div[3]/div/div[1]/span')
                    total_results = driver.find_element(By.CLASS_NAME, 'materialOverride_STCNx toolbarTitle_2lgWp')
                    print(f'TOTAL RESULTS: {total_results.get_text()}')
                    if total_results.get_text() == '0 results':
                        return 404
                    else:
                        print('FLAG 9')
                except NoSuchElementException:
                    print('FLAG 8')
        except (ConnectionRefusedError, MaxRetryError) as e:
            print('FLAG 5')
            return 404
