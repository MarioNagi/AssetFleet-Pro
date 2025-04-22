# tracking/tasks.py

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from .models import Tool, Car
from django.template.loader import render_to_string
from django.conf import settings

@shared_task
def send_calibration_reminders():
    today = timezone.now().date()
    upcoming_tools = Tool.objects.filter(calibration_date__lte=today + timezone.timedelta(days=7))
    for tool in upcoming_tools:
        subject = f"Calibration Reminder: {tool.name}"
        message = render_to_string('emails/calibration_reminder.html', {'tool': tool})
        recipient_list = [tool.assigned_user.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

@shared_task
def send_rego_reminders():
    today = timezone.now().date()
    upcoming_cars = Car.objects.filter(rego_expiry_date__lte=today + timezone.timedelta(days=30))
    for car in upcoming_cars:
        subject = f"Registration Expiry Reminder: {car.rego}"
        message = render_to_string('emails/rego_reminder.html', {'car': car})
        recipient_list = [car.assigned_user.email]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
