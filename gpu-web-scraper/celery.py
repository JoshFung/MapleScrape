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
    # executes every 10 minute
    'scraping-task-ten-min': {
        'task': 'scraping.tasks.scrape',
        'schedule': crontab(minute='*/10')
    }
}
