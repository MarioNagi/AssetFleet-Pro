from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tracking.models import Profile, Tool, Car, Maintenance, OdometerReading, Transfer, FuelRecord
from django.utils import timezone
from datetime import timedelta
import random
import faker
import os
from django.core.management.utils import get_random_secret_key

fake = faker.Faker()

class Command(BaseCommand):
    help = 'Generates sample data for demonstration purposes'

    def handle(self, *args, **kwargs):
        # Check if we're in development environment
        if not os.getenv('DJANGO_DEBUG', 'False').lower() == 'true':
            self.stdout.write(self.style.ERROR('This command can only be run in development environment'))
            return

        self.stdout.write('Generating sample data...')
        
        # Create demo users
        users = self._create_users()
        
        # Create tools
        tools = self._create_tools(users)
        
        # Create vehicles
        cars = self._create_cars(users)
        
        # Create maintenance records
        self._create_maintenance_records(cars)
        
        # Create odometer readings
        self._create_odometer_readings(cars)
        
        # Create fuel records
        self._create_fuel_records(cars)
        
        # Create transfers
        self._create_transfers(users, tools, cars)
        
        self.stdout.write(self.style.SUCCESS('Successfully generated sample data'))

    def _create_users(self):
        users = []
        
        # Create one admin user with secure password from environment or generate secure one
        admin_password = os.getenv('DEMO_ADMIN_PASSWORD') or get_random_secret_key()[:16]
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password=admin_password
        )
        self.stdout.write(f'Created admin user with password: {admin_password}')
        
        Profile.objects.filter(user=admin).update(
            access_level='Admin',
            state='R1'
        )
        users.append(admin)
        
        # Create managers with secure passwords
        for region in ['R1', 'R2', 'R3']:
            manager_password = get_random_secret_key()[:16]
            manager = User.objects.create_user(
                username=f'manager_{region.lower()}',
                email=f'manager_{region.lower()}@example.com',
                password=manager_password,
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            self.stdout.write(f'Created manager_{region.lower()} with password: {manager_password}')
            
            Profile.objects.filter(user=manager).update(
                access_level='Manager',
                state=region
            )
            users.append(manager)
        
        # Create regular users with secure passwords
        for i in range(10):
            user_password = get_random_secret_key()[:16]
            user = User.objects.create_user(
                username=f'user_{i+1}',
                email=f'user_{i+1}@example.com',
                password=user_password,
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            self.stdout.write(f'Created user_{i+1} with password: {user_password}')
            
            Profile.objects.filter(user=user).update(
                access_level='User',
                state=random.choice(['R1', 'R2', 'R3', 'R4', 'R5'])
            )
            users.append(user)
        
        return users

    def _create_tools(self, users):
        tools = []
        tool_types = [choice[0] for choice in Tool._meta.get_field('tool_name').choices]
        brands = ['DeWalt', 'Milwaukee', 'Makita', 'Bosch', 'Stanley', 'Klein Tools']
        
        # Keep track of used numbers to ensure uniqueness
        used_internal_numbers = set()
        used_serial_numbers = set()
        
        for i in range(30):
            # Generate unique internal number
            while True:
                internal_number = f'TOOL-{i+1:04d}'
                if internal_number not in used_internal_numbers:
                    used_internal_numbers.add(internal_number)
                    break
            
            # Generate unique serial number (some tools may not have one)
            serial_number = None
            if random.random() > 0.3:  # 70% chance of having a serial number
                while True:
                    new_serial = f'SN-{fake.uuid4()[:8].upper()}'
                    if new_serial not in used_serial_numbers:
                        serial_number = new_serial
                        used_serial_numbers.add(new_serial)
                        break
            
            tool = Tool.objects.create(
                internal_number=internal_number,
                serial_number=serial_number,
                tool_name=random.choice(tool_types),
                brand=random.choice(brands),
                description=fake.sentence(),
                size=random.choice(['Small', 'Medium', 'Large', '']),
                calibration_date=timezone.now().date() + timedelta(days=random.randint(-180, 180)),
                store=random.choice(['authorized_dealer', 'retail_store', 'online_store']),
                state=random.choice(['R1', 'R2', 'R3', 'R4', 'R5']),
                quantity=random.randint(1, 5),
                estimated_cost=random.uniform(50, 2000),
                assigned_user=random.choice(users) if random.random() > 0.2 else None
            )
            tools.append(tool)
        
        return tools

    def _create_cars(self, users):
        cars = []
        makes = ['Toyota', 'Ford', 'Hyundai', 'Mitsubishi', 'Isuzu']
        models = {
            'Toyota': ['Hilux', 'HiAce', 'RAV4', 'Corolla'],
            'Ford': ['Ranger', 'Transit', 'Escape', 'Focus'],
            'Hyundai': ['iLoad', 'Santa Fe', 'Tucson', 'i30'],
            'Mitsubishi': ['Triton', 'Outlander', 'ASX', 'Express'],
            'Isuzu': ['D-Max', 'MU-X', 'N Series', 'F Series']
        }
        
        # Keep track of used numbers
        used_regos = set()
        used_vins = set()
        
        for i in range(20):
            make = random.choice(makes)
            model = random.choice(models[make])
            purchase_date = timezone.now().date() - timedelta(days=random.randint(30, 730))
            
            # Generate unique rego
            while True:
                rego = f"{random.choice(['ABC', 'XYZ', 'DEF'])}{random.randint(100, 999)}"
                if rego not in used_regos:
                    used_regos.add(rego)
                    break
            
            # Generate unique VIN
            while True:
                vin = f"VIN{fake.uuid4()[:6].upper()}{''.join(random.choices('0123456789ABCDEFGHIJKLMNPQRSTUVWXYZ', k=10))}"
                if vin not in used_vins:
                    used_vins.add(vin)
                    break
            
            car = Car.objects.create(
                rego=rego,
                rego_expiry_date=timezone.now().date() + timedelta(days=random.randint(30, 365)),
                purchase_date=purchase_date,
                purchase_price=random.uniform(25000, 75000),
                state=random.choice(['R1', 'R2', 'R3', 'R4', 'R5']),
                assigned_user=random.choice(users) if random.random() > 0.2 else None,
                maintenance_sticker_date=timezone.now().date() + timedelta(days=random.randint(-30, 180)),
                make=make,
                model=model,
                vin_number=vin,
                manufacturing_year=random.randint(2018, 2024),
                color=random.choice(['White', 'Silver', 'Black', 'Blue', 'Red']),
                body=random.choice(['Sedan', 'SUV', 'Ute', 'Van', 'Truck']),
                next_service_date=timezone.now().date() + timedelta(days=random.randint(-30, 180)),
                service_interval_km=10000,
                last_service_km=random.randint(10000, 50000)
            )
            cars.append(car)
        
        return cars

    def _create_maintenance_records(self, cars):
        service_types = ['regular', 'repair', 'inspection', 'accident', 'other']
        service_providers = ['AutoCare Plus', 'QuickFix Mechanics', 'MainDealership Service', 'Mobile Mechanic']
        
        for car in cars:
            num_records = random.randint(2, 6)
            last_odo = car.last_service_km or 0
            
            for _ in range(num_records):
                service_date = timezone.now().date() - timedelta(days=random.randint(0, 365))
                odo_reading = last_odo + random.randint(5000, 15000)
                
                Maintenance.objects.create(
                    car=car,
                    service_date=service_date,
                    odometer_reading=odo_reading,
                    service_type=random.choice(service_types),
                    service_provider=random.choice(service_providers),
                    description=fake.paragraph(),
                    total_cost=random.uniform(200, 2000)
                )
                
                last_odo = odo_reading

    def _create_odometer_readings(self, cars):
        for car in cars:
            last_reading = car.last_service_km or 0
            num_readings = random.randint(6, 12)
            
            for i in range(num_readings):
                reading_date = timezone.now().date() - timedelta(days=i*30)
                reading_value = last_reading + random.randint(1000, 3000)
                
                OdometerReading.objects.create(
                    car=car,
                    reading_date=reading_date,
                    reading_value=reading_value
                )
                
                last_reading = reading_value

    def _create_fuel_records(self, cars):
        stations = ['Shell', 'BP', 'Caltex', 'United', '7-Eleven']
        
        for car in cars:
            num_records = random.randint(8, 16)
            last_odo = car.last_service_km or 0
            
            for i in range(num_records):
                date = timezone.now().date() - timedelta(days=i*15)
                odo = last_odo + random.randint(300, 800)
                liters = random.uniform(40, 80)
                cost_per_liter = random.uniform(1.5, 2.2)
                
                FuelRecord.objects.create(
                    car=car,
                    date=date,
                    odometer=odo,
                    liters=liters,
                    cost_per_liter=cost_per_liter,
                    total_cost=liters * cost_per_liter,
                    fuel_type=random.choice(['diesel', 'petrol_91', 'petrol_95']),
                    station=random.choice(stations),
                    full_tank=random.random() > 0.2
                )
                
                last_odo = odo

    def _create_transfers(self, users, tools, cars):
        num_transfers = min(len(tools) + len(cars), 30)
        
        for _ in range(num_transfers):
            if random.random() > 0.5 and tools:
                item = random.choice(tools)
                transfer_type = 'Tool'
                item_id = item.internal_number
            elif cars:
                item = random.choice(cars)
                transfer_type = 'Car'
                item_id = item.id
            else:
                continue
                
            from_user = random.choice(users)
            to_user = random.choice([u for u in users if u != from_user])
            
            Transfer.objects.create(
                transfer_type=transfer_type,
                item_id=item_id,
                from_user=from_user,
                to_user=to_user,
                date_of_transfer=timezone.now().date() - timedelta(days=random.randint(0, 180))
            )