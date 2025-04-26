from django.core.management.base import BaseCommand
import pandas as pd
from django.contrib.auth.models import User
from tracking.models import Car
from django.utils import timezone

class Command(BaseCommand):
    help = 'Import cars from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to the Excel file')

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        
        try:
            df = pd.read_excel(excel_file)
            required_columns = [
                'rego', 'rego_expiry_date', 'state', 'make', 'model', 
                'vin_number', 'manufacturing_year', 'color', 'body',
                'assigned_user', 'maintenance_sticker_date'
            ]
            
            # Optional columns
            optional_columns = [
                'purchase_date', 'purchase_price', 'service_interval_km',
                'last_service_km', 'photo'
            ]
            
            # Validate required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                self.stdout.write(
                    self.style.ERROR(
                        f'Missing required columns: {", ".join(missing_columns)}'
                    )
                )
                return

            for _, row in df.iterrows():
                try:
                    # Get assigned user
                    try:
                        assigned_user = User.objects.get(username=row['assigned_user'])
                    except User.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f'User {row["assigned_user"]} not found, skipping car {row["rego"]}'
                            )
                        )
                        continue

                    # Prepare car data
                    car_data = {
                        'rego': row['rego'],
                        'rego_expiry_date': pd.to_datetime(row['rego_expiry_date']).date(),
                        'state': row['state'].upper(),
                        'make': row['make'],
                        'model': row['model'],
                        'vin_number': row['vin_number'],
                        'manufacturing_year': row['manufacturing_year'],
                        'color': row['color'],
                        'body': row['body'],
                        'assigned_user': assigned_user,
                        'maintenance_sticker_date': pd.to_datetime(row['maintenance_sticker_date']).date(),
                    }

                    # Add optional fields if present
                    if 'purchase_date' in df.columns and pd.notna(row['purchase_date']):
                        car_data['purchase_date'] = pd.to_datetime(row['purchase_date']).date()
                    if 'purchase_price' in df.columns and pd.notna(row['purchase_price']):
                        car_data['purchase_price'] = row['purchase_price']
                    if 'service_interval_km' in df.columns and pd.notna(row['service_interval_km']):
                        car_data['service_interval_km'] = row['service_interval_km']
                    if 'last_service_km' in df.columns and pd.notna(row['last_service_km']):
                        car_data['last_service_km'] = row['last_service_km']

                    # Create or update car
                    car, created = Car.objects.update_or_create(
                        rego=row['rego'],
                        defaults=car_data
                    )

                    action = 'Created' if created else 'Updated'
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'{action} car: {car.rego}'
                        )
                    )

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error processing car {row["rego"]}: {str(e)}'
                        )
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading Excel file: {str(e)}')
            )