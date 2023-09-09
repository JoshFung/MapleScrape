import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gpu-web-scraper.settings')

app = Celery('gpu-web-scraper')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='celery')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    # 'scraping-task-on-startup-and-every-min': {
    #     'task': 'scraping.tasks.scrape',
    #     'schedule': crontab(),  # Run immediately on startup and every minute after
    # },
    # 'scraping-task-every-five-minutes': {
    #     'task': 'scraping.tasks.scrape',
    #     'schedule': crontab(minute='*/5'),  # Run every 5 minutes
    # },
    # 'scraping-task-every-ten-minutes': {
    #     'task': 'scraping.tasks.scrape',
    #     'schedule': crontab(minute='*/10'),  # Run every 10 minutes
    # },
    'scraping-task-at-midnight': {
        'task': 'scraping.tasks.scrape',
        'schedule': crontab(minute=0, hour=0),  # Run every 10 minutes
    }
}
