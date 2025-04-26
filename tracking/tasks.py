# tracking/tasks.py

from celery import shared_task
from django.core.management import call_command
from django.conf import settings
from datetime import datetime
import boto3
import logging
import os

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def backup_database(self):
    """Task to backup the database and upload to S3"""
    try:
        # Create backups directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{timestamp}.json')

        # Create database backup
        with open(backup_file, 'w') as f:
            call_command('dumpdata', '--exclude', 'contenttypes', '--exclude', 'auth.permission', 
                        '--natural-foreign', '--indent', '2', stdout=f)

        # Upload to S3 if configured
        if settings.AWS_STORAGE_BUCKET_NAME:
            try:
                s3 = boto3.client('s3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )
                
                s3_path = f'backups/database/backup_{timestamp}.json'
                s3.upload_file(backup_file, settings.AWS_STORAGE_BUCKET_NAME, s3_path)
                
                # Keep only last 30 backups in S3
                response = s3.list_objects_v2(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Prefix='backups/database/'
                )
                
                if 'Contents' in response:
                    files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
                    for file in files[30:]:  # Keep only last 30 files
                        s3.delete_object(
                            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                            Key=file['Key']
                        )
                
                logger.info(f"Database backup uploaded to S3: {s3_path}")
            
            except Exception as e:
                logger.error(f"Error uploading backup to S3: {str(e)}")
                raise

        # Cleanup local backup file
        if os.path.exists(backup_file):
            os.remove(backup_file)
        
        logger.info("Database backup completed successfully")
        
    except Exception as e:
        logger.error(f"Database backup failed: {str(e)}")
        raise self.retry(exc=e)

@shared_task
def check_calibration_dates():
    """Check for tools nearing calibration date and send notifications"""
    from .models import Tool
    from django.utils import timezone
    from datetime import timedelta
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    
    # Check tools due for calibration in next 30 days
    threshold_date = timezone.now().date() + timedelta(days=30)
    due_tools = Tool.objects.filter(
        calibration_date__lte=threshold_date,
        calibration_date__gte=timezone.now().date()
    )
    
    for tool in due_tools:
        if tool.assigned_user and tool.assigned_user.email:
            context = {
                'tool': tool,
                'days_remaining': (tool.calibration_date - timezone.now().date()).days
            }
            
            html_message = render_to_string('emails/calibration_reminder.html', context)
            
            try:
                send_mail(
                    subject=f'Tool Calibration Due: {tool.internal_number}',
                    message=strip_tags(html_message),
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[tool.assigned_user.email],
                    fail_silently=False
                )
                logger.info(f"Calibration reminder sent for tool {tool.internal_number}")
            except Exception as e:
                logger.error(f"Failed to send calibration reminder for tool {tool.internal_number}: {str(e)}")

@shared_task
def check_maintenance_dates():
    """Check for vehicles due for maintenance and send notifications"""
    from .models import Car
    from django.utils import timezone
    from datetime import timedelta
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    
    # Check cars due for maintenance in next 14 days or by odometer
    threshold_date = timezone.now().date() + timedelta(days=14)
    due_cars = Car.objects.filter(
        next_service_date__lte=threshold_date,
        next_service_date__gte=timezone.now().date()
    )
    
    for car in due_cars:
        if car.assigned_user and car.assigned_user.email:
            context = {
                'car': car,
                'days_remaining': (car.next_service_date - timezone.now().date()).days,
                'is_km_due': car.is_service_due_by_km()
            }
            
            html_message = render_to_string('emails/maintenance_reminder.html', context)
            
            try:
                send_mail(
                    subject=f'Vehicle Maintenance Due: {car.rego}',
                    message=strip_tags(html_message),
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[car.assigned_user.email],
                    fail_silently=False
                )
                logger.info(f"Maintenance reminder sent for vehicle {car.rego}")
            except Exception as e:
                logger.error(f"Failed to send maintenance reminder for vehicle {car.rego}: {str(e)}")

@shared_task
def check_rego_expiry():
    """Check for vehicles with approaching registration expiry and send notifications"""
    from .models import Car
    from django.utils import timezone
    from datetime import timedelta
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    
    # Check cars with rego expiring in next 30 days
    threshold_date = timezone.now().date() + timedelta(days=30)
    expiring_cars = Car.objects.filter(
        rego_expiry_date__lte=threshold_date,
        rego_expiry_date__gte=timezone.now().date()
    )
    
    for car in expiring_cars:
        if car.assigned_user and car.assigned_user.email:
            context = {
                'car': car,
                'days_remaining': (car.rego_expiry_date - timezone.now().date()).days
            }
            
            html_message = render_to_string('emails/rego_reminder.html', context)
            
            try:
                send_mail(
                    subject=f'Vehicle Registration Expiring: {car.rego}',
                    message=strip_tags(html_message),
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[car.assigned_user.email],
                    fail_silently=False
                )
                logger.info(f"Registration reminder sent for vehicle {car.rego}")
            except Exception as e:
                logger.error(f"Failed to send registration reminder for vehicle {car.rego}: {str(e)}")
