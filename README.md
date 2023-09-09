# MapleScrape

![Example Screenshot](<assets/MapleScrape Screenshot.png>)

<!-- ABOUT THE PROJECT -->

## About The Project

Simplistic web scraping function to help retrieve information of graphics cards from sites such as Newegg, Best Buy, and Canada Computers.

The data scraped by the function is locally stored in a JSON file named based on the time which the scraping process occurs. Furthermore, this data is saved into SQLite to be used on the site.

It is suggested to make use of Celery to have scheduled scraping, default scheduling being every midnight. Otherwise, it is also possible to have individual runs.

NOTE: Don't let your computer sleep otherwise it may cause the scraping process to abruptly stop

### Built With

- Selenium
- BeautifulSoup4
- Pandas
- lxml
- SQLite3
- Django
- Chromedriver
- Celery

<!-- GETTING STARTED -->

## Getting Started

### Install the required packages using:

```sh
pip install -r requirements.txt
```

### Set your `.env` variables

```
SECRET_KEY -> Django secret key
CHROME_PATH -> Absolute path to Google Chrome
CHROMEDRIVER_PATH -> Absolute path to Chromedriver
NEWEGG_URL -> URL for Newegg GPUs
BEST_BUY_URL -> URL for Best Buy GPUs
CANADA_COMPUTERS_URL -> URL for Canada Computers GPUs
```

Ensure the URLs you set are for the GPU pages of the respective sites.

For example:

- [Newegg](https://www.newegg.ca/Desktop-Graphics-Cards/SubCategory/ID-48?Tid=7708&PageSize=96)
- [Best Buy](https://www.bestbuy.ca/en-ca/category/graphics-cards/20397)
- [Canada Computers](https://www.canadacomputers.com/index.php?cPath=43)

### Run the scraping process

There are three ways of running the scraping process:

#### With Celery and RabbitMQTT on a schedule

1. Make sure you install RabbitMQTT
2. Start up RabbitMQ using `sudo rabbitmq-server` in a terminal
   1. Wait until it completes when message `Starting broker... completed with x plugins`
3. Start up the actual service with the Celery command: `celery -A gpu-web-scraper worker -B -l INFO`
   1. `-A gpu-web-scraper` specifies which project
   2. `-B` tells it to run on the given beat schedule
   3. `-l INFO` tells it log information

#### With Celery and RabbitMQTT without a schedule

1. Do the same first two steps as above
2. Start up the Celery service using: `celery -A gpu-web-scraper worker -l INFO`
   - Note that we don't use `-B` as we don't want it on a service
3. Open up a third terminal
4. Import the Django settings module using `export DJANGO_SETTINGS_MODULE=gpu-web-scraper.settings`
5. Enter the Python console and run the following:

   ```
   import django
   django.setup()
   from scraping.tasks import scrape
   scrape.apply_async()
   ```

Note: You can end RabbitMQTT service using `rabbitmqctl stop`

#### Without Celery and RabbitMQTT

1. Import the Django settings module using `export DJANGO_SETTINGS_MODULE=gpu-web-scraper.settings`
2. Enter the Python console and run the following:

   ```
   import django
   django.setup()
   from scraping.tasks import scrape
   scrape()
   ```

### Collect the static files and run the site

Run the following commands:

1. `python3 manage.py collectstatic` (not required)
2. `python3 manage.py makemigrations` (if made changes to model)
3. `python3 manage.py migrate`
4. `python3 manage.py runserver`

## Future Goals

- Make use of Docker to always have the server running
- Save backups of data online
