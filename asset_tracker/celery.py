from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')

app = Celery('asset_tracker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'check-calibration-dates': {
        'task': 'tracking.tasks.check_calibration_dates',
        'schedule': crontab(hour=7, minute=30),  # Run daily at 7:30 AM
    },
    'check-maintenance-dates': {
        'task': 'tracking.tasks.check_maintenance_dates',
        'schedule': crontab(hour=7, minute=0),  # Run daily at 7:00 AM
    },
    'check-rego-expiry': {
        'task': 'tracking.tasks.check_rego_expiry',
        'schedule': crontab(hour=8, minute=0),  # Run daily at 8:00 AM
    },
    'backup-database': {
        'task': 'tracking.tasks.backup_database',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}

# Celery Configuration
app.conf.update(
    # Broker settings
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    
    # Security settings
    security_key=os.getenv('CELERY_SECURITY_KEY', settings.SECRET_KEY),
    
    # Worker settings
    worker_max_tasks_per_child=1000,
    worker_max_memory_per_child=200000,  # 200MB
    
    # Task execution settings
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    
    # Queue settings
    task_default_queue='default',
    task_queues={
        'default': {},
        'high-priority': {},
        'low-priority': {},
    },
    
    # Result settings
    task_ignore_result=True,
    result_expires=3600,  # 1 hour
    
    # Error handling
    task_reject_on_worker_lost=True,
    task_acks_late=True,
)
