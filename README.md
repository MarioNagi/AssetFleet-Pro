# Asset Tracker

A comprehensive Django-based asset management system for tracking fleet vehicles and tools, managing maintenance schedules, and monitoring asset usage.

## Features

- **Vehicle Management**
  - Track car details and ownership
  - Monitor odometer readings
  - Manage vehicle transfers
  - Vehicle maintenance scheduling and history
  - Registration renewal tracking

- **Tool Management**
  - Tool inventory tracking
  - Tool transfer management
  - Maintenance scheduling

- **Analytics & Reporting**
  - Fleet analytics dashboard
  - Manager-specific views
  - Custom reporting tools

- **User Management**
  - Role-based access control
  - Admin dashboard
  - Manager dashboard
  - User dashboard

- **Automated Notifications**
  - Maintenance reminders
  - Registration renewal alerts
  - Calibration reminders
  - Tire service notifications

## Technologies Used

- Django
- Celery (for background tasks)
- Bootstrap
- SQLite
- Docker
- Nginx
- Gunicorn

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```
   python manage.py migrate
   ```
5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```
   python manage.py runserver
   ```

## Docker Deployment

The project includes Docker configuration for easy deployment:

```
docker-compose up --build
```

## Project Structure

- `asset_tracker/` - Main project configuration
- `tracking/` - Main application code
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)
- `media/` - User-uploaded files
- `logs/` - Application logs

## Contributing

Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
