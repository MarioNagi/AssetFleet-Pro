from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver


# --------- Profile Model ---------
class Profile(models.Model):
    ACCESS_LEVELS = [
        ('User', 'User'),
        ('Manager', 'Manager'),
        ('Admin', 'Admin'),
    ]
    
    STATE_CHOICES = [
        ('NSW', 'New South Wales'),
        ('VIC', 'Victoria'),
        ('QLD', 'Queensland'),
        ('WA', 'Western Australia'),
        ('SA', 'South Australia'),
        ('TAS', 'Tasmania'),
        ('NT', 'Northern Territory'),
        ('ACT', 'Australian Capital Territory'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=10, choices=ACCESS_LEVELS, default='User')
    state = models.CharField(
        max_length=15,
        choices=STATE_CHOICES,
        blank=True,
        null=True
    )
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# --------- Tool Model ---------
class Tool(models.Model):
    internal_number = models.CharField(max_length=100, primary_key=True, unique=True, blank=True, db_index=True)
    serial_number = models.CharField(max_length=100, unique=True, blank=True, null=True, db_index=True)
    tool_name = models.CharField(max_length=100, choices=[
        # Safety Equipment
        ('safety_harness', 'Safety Harness'),
        ('safety_helmet', 'Safety Helmet'),
        ('safety_glasses', 'Safety Glasses'),
        ('safety_gloves', 'Safety Gloves'),
        ('first_aid_kit', 'First Aid Kit'),
        ('fire_extinguisher', 'Fire Extinguisher'),
        ('rescue_kit', 'Rescue Kit'),
        ('spill_kit', 'Spill Kit'),
        
        # Hand Tools
        ('screwdriver_set', 'Screwdriver Set'),
        ('wrench_set', 'Wrench Set'),
        ('plier_set', 'Plier Set'),
        ('hammer', 'Hammer'),
        ('measuring_tape', 'Measuring Tape'),
        
        # Power Tools
        ('drill_cordless', 'Cordless Drill'),
        ('impact_driver', 'Impact Driver'),
        ('angle_grinder', 'Angle Grinder'),
        ('heat_gun', 'Heat Gun'),
        
        # Specialized Tools
        ('multimeter', 'Multimeter'),
        ('cable_tester', 'Cable Tester'),
        ('crimping_tool', 'Crimping Tool'),
        ('laser_level', 'Laser Level'),
        
        # IT Equipment
        ('laptop', 'Laptop'),
        ('printer', 'Printer'),
        ('label_maker', 'Label Maker'),
        ('barcode_scanner', 'Barcode Scanner'),
        
        # Storage & Transport
        ('tool_box', 'Tool Box'),
        ('tool_bag', 'Tool Bag'),
        ('ladder', 'Ladder'),
        ('trolley', 'Trolley'),
        
        # Site Equipment
        ('generator', 'Generator'),
        ('lighting_equipment', 'Lighting Equipment'),
        ('traffic_cone', 'Traffic Cone'),
        ('warning_sign', 'Warning Sign'),
        
        # Other
        ('other', 'Other')
    ], db_index=True)
    
    brand = models.CharField(max_length=100, default='Generic Brand')
    description = models.TextField(blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    calibration_date = models.DateField(null=True, blank=True)
    
    store = models.CharField(
        max_length=50,
        choices=[
            ('authorized_dealer', 'Authorized Dealer'),
            ('retail_store', 'Retail Store'),
            ('online_store', 'Online Store'),
            ('other', 'Other')
        ]
    )
    
    state = models.CharField(
        max_length=50,
        choices=Profile.STATE_CHOICES,  # Use the same choices as Profile model
        default='NSW'
    )
    
    quantity = models.PositiveIntegerField(default=1)
    photo = models.ImageField(upload_to='tool_photos/', blank=True, null=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tools')
    assigned_car = models.ForeignKey('Car', on_delete=models.SET_NULL, null=True, blank=True, related_name='tools')

    def __str__(self):
        return f"{self.tool_name} - {self.internal_number}"

@receiver(pre_save, sender=Tool)
def add_default_internal_number(sender, instance, **kwargs):
    if not instance.internal_number:
        last_tool = Tool.objects.filter(internal_number__startswith='TOOL-').order_by('-internal_number').first()
        if last_tool and last_tool.internal_number.startswith('TOOL-'):
            try:
                last_number = int(last_tool.internal_number.replace('TOOL-', '') or 0)
                instance.internal_number = f"TOOL-{str(last_number + 1).zfill(4)}"
            except ValueError:
                instance.internal_number = "TOOL-0001"
        else:
            instance.internal_number = "TOOL-0001"


# --------- Car Model ---------
class Car(models.Model):
    STATE_CHOICES = [
        ('NSW', 'New South Wales'),
        ('VIC', 'Victoria'),
        ('QLD', 'Queensland'),
        ('WA', 'Western Australia'),
        ('SA', 'South Australia'),
        ('TAS', 'Tasmania'),
        ('NT', 'Northern Territory'),
        ('ACT', 'Australian Capital Territory'),
    ]
    
    BODY_CHOICES = [
        ('Sedan', 'Sedan'),
        ('Hatchback', 'Hatchback'),
        ('SUV', 'SUV'),
        ('Ute', 'Ute'),
        ('Van', 'Van'),
        ('Truck', 'Truck'),
        ('EWP', 'EWP'),
        ('Trailer', 'Trailer'),
        ('Other', 'Other')
    ]

    rego = models.CharField(max_length=20, unique=True, db_index=True)  # Add db_index
    rego_expiry_date = models.DateField()
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='NSW', db_index=True)  # Add db_index
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cars', db_index=True)  # Add db_index
    maintenance_sticker_date = models.DateField()
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    vin_number = models.CharField(max_length=100, unique=True)
    manufacturing_year = models.PositiveIntegerField(null=True, blank=True)  # New field for manufacturing year
    color = models.CharField(max_length=30, blank=True, null=True)  # New field for color
    body = models.CharField(max_length=50, choices=BODY_CHOICES, default='Sedan')  # New field for car body type
    photo = models.ImageField(upload_to='car_photos/', null=True, blank=True)
    
    # Maintenance related fields
    next_service_date = models.DateField(null=True, blank=True)
    service_interval_km = models.PositiveIntegerField(default=10000)
    last_service_km = models.PositiveIntegerField(null=True, blank=True)
    monthly_odometer_check = models.BooleanField(default=True)
    total_maintenance_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    
    def is_service_due(self):
        if not self.next_service_date:
            return False
        return timezone.now().date() >= self.next_service_date

    def is_service_due_by_km(self):
        if not self.last_service_km:
            return False
        latest_reading = self.odometer_readings.first()
        if not latest_reading:
            return False
        return (latest_reading.reading_value - self.last_service_km) >= self.service_interval_km

    def get_latest_odometer(self):
        """Get the latest odometer reading."""
        return self.odometer_readings.order_by('-reading_date').first()

    def get_current_km(self):
        """Get current odometer reading value."""
        latest = self.get_latest_odometer()
        return latest.reading_value if latest else 0

    def get_km_since_service(self):
        """Calculate kilometers driven since last service."""
        if not self.last_service_km:
            return None
        latest = self.get_latest_odometer()
        if not latest:
            return None
        return latest.reading_value - self.last_service_km

    def get_service_status(self):
        """Get detailed service status."""
        km_since_service = self.get_km_since_service()
        days_to_service = (self.next_service_date - timezone.now().date()).days if self.next_service_date else None
        
        return {
            'km_since_service': km_since_service,
            'km_until_service': self.service_interval_km - km_since_service if km_since_service else None,
            'days_to_service': days_to_service,
            'service_due': self.is_service_due() or self.is_service_due_by_km(),
            'next_service_date': self.next_service_date
        }

    def get_maintenance_costs(self, start_date=None, end_date=None):
        """Get maintenance costs for a specific period."""
        records = self.maintenance_records.all()
        if start_date:
            records = records.filter(service_date__gte=start_date)
        if end_date:
            records = records.filter(service_date__lte=end_date)
        
        total_cost = sum(record.total_cost for record in records)
        return {
            'total_cost': total_cost,
            'record_count': records.count(),
            'records': records
        }

    def get_fuel_efficiency(self, last_n_records=5):
        """Calculate average fuel efficiency from last N full tank records."""
        fuel_records = self.fuel_records.filter(full_tank=True).order_by('-date')[:last_n_records]
        efficiencies = [r.fuel_efficiency for r in fuel_records if r.fuel_efficiency]
        
        if not efficiencies:
            return None
            
        return {
            'current': efficiencies[0] if efficiencies else None,
            'average': sum(efficiencies) / len(efficiencies) if efficiencies else None,
            'best': min(efficiencies) if efficiencies else None,
            'worst': max(efficiencies) if efficiencies else None
        }

    def get_total_costs(self, start_date=None, end_date=None):
        """Calculate total costs including maintenance and fuel."""
        maintenance_data = self.get_maintenance_costs(start_date, end_date)
        
        fuel_records = self.fuel_records.all()
        if start_date:
            fuel_records = fuel_records.filter(date__gte=start_date)
        if end_date:
            fuel_records = fuel_records.filter(date__lte=end_date)
        
        fuel_cost = sum(record.total_cost for record in fuel_records)
        
        return {
            'maintenance_cost': maintenance_data['total_cost'],
            'fuel_cost': fuel_cost,
            'total_cost': maintenance_data['total_cost'] + fuel_cost
        }

    def get_tire_status(self):
        """Get status of current tires."""
        latest_record = self.tire_records.order_by('-change_date').first()
        if not latest_record:
            return None
            
        current_km = self.get_current_km()
        km_since_change = current_km - latest_record.change_date_km if current_km else None
        
        return {
            'last_change_date': latest_record.change_date,
            'km_since_change': km_since_change,
            'km_until_change': latest_record.next_change_km - current_km if current_km else None,
            'tire_positions': latest_record.tire_positions,
            'change_due': current_km >= latest_record.next_change_km if current_km else False
        }

    def __str__(self):
        return f"{self.make} {self.model} ({self.rego})"

    class Meta:
        ordering = ['rego']
        indexes = [
            models.Index(fields=['rego']),
            models.Index(fields=['state']),
            models.Index(fields=['assigned_user']),
        ]


# --------- TireRecord Model ---------
class TireRecord(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='tire_records')
    change_date = models.DateField()
    next_change_km = models.PositiveIntegerField()
    alignment_done = models.BooleanField(default=False)
    tire_positions = models.JSONField(default=dict)  # {'FL': 'New', 'FR': 'Good', 'RL': 'Worn', 'RR': 'Replaced'}
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Tire service for {self.car.rego} on {self.change_date}"


# --------- Maintenance Model ---------
class Maintenance(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='maintenance_records')
    service_date = models.DateField(default=timezone.now)
    odometer_reading = models.PositiveIntegerField(default=0)
    service_type = models.CharField(
        max_length=50, 
        choices=[
            ('regular', 'Regular Service'),
            ('repair', 'Repair'),
            ('inspection', 'Inspection'),
            ('accident', 'Accident Repair'),
            ('other', 'Other')
        ],
        default='regular'
    )
    invoice_number = models.CharField(max_length=100, blank=True, default='')
    service_provider = models.CharField(max_length=200, default='Unknown Provider')
    description = models.TextField(default='')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    documents = models.FileField(upload_to='maintenance_docs/', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Update car's last service info
        if self.service_type == 'regular':
            self.car.last_service_km = self.odometer_reading
            self.car.next_service_date = self.service_date + timezone.timedelta(days=180)  # 6 months
            self.car.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.service_type} for {self.car.rego} on {self.service_date}"


# --------- MaintenanceItem Model ---------
class MaintenanceItem(models.Model):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE, related_name='items')
    item_type = models.CharField(max_length=50, choices=[
        ('parts', 'Parts'),
        ('labor', 'Labor'),
        ('consumables', 'Consumables'),
        ('other', 'Other')
    ],default='parts')
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    
    @property
    def total_cost(self):
        return self.quantity * self.unit_cost

    def __str__(self):
        return f"{self.description} - ${self.total_cost}"


# --------- Odometer Reading ---------
class OdometerReading(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='odometer_readings', db_index=True)  # Add db_index
    reading_date = models.DateField(default=timezone.now)
    reading_value = models.PositiveIntegerField()

    class Meta:
        ordering = ['-reading_date']

    def __str__(self):
        return f"{self.car.rego} - {self.reading_date}: {self.reading_value} km"


# --------- Transfer Model ---------
class Transfer(models.Model):
    TRANSFER_TYPE_CHOICES = [('Tool', 'Tool'), ('Car', 'Car')]

    transfer_type = models.CharField(max_length=10, choices=TRANSFER_TYPE_CHOICES)
    item_id = models.PositiveIntegerField()
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transfers_from')
    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transfers_to')
    date_of_transfer = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.transfer_type} Transfer on {self.date_of_transfer}"


# --------- FuelRecord Model ---------
class FuelRecord(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='fuel_records')
    date = models.DateField()
    odometer = models.PositiveIntegerField()
    liters = models.DecimalField(max_digits=6, decimal_places=2)
    cost_per_liter = models.DecimalField(max_digits=4, decimal_places=2)
    total_cost = models.DecimalField(max_digits=8, decimal_places=2)
    fuel_type = models.CharField(max_length=20, choices=[
        ('diesel', 'Diesel'),
        ('petrol_91', 'Petrol 91'),
        ('petrol_95', 'Petrol 95'),
        ('petrol_98', 'Petrol 98'),
        ('lpg', 'LPG')
    ])
    station = models.CharField(max_length=100, blank=True)
    full_tank = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        self.total_cost = self.liters * self.cost_per_liter
        super().save(*args, **kwargs)

    @property
    def fuel_efficiency(self):
        """Calculate fuel efficiency in L/100km"""
        previous_record = FuelRecord.objects.filter(
            car=self.car,
            date__lt=self.date,
            full_tank=True
        ).order_by('-date').first()
        
        if previous_record and previous_record.odometer < self.odometer:
            distance = self.odometer - previous_record.odometer
            return (self.liters * 100) / distance
        return None

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.car.rego} - {self.date} - {self.liters}L"
