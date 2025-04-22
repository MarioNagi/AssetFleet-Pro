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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_level = models.CharField(max_length=10, choices=ACCESS_LEVELS, default='User')
    state = models.CharField(
        max_length=10,
        choices=[('NSW', 'NSW'), ('VIC', 'VIC'), ('WA', 'WA'), ('SA', 'SA'), ('QLD', 'QLD'), ('TZ', 'TZ')],
        blank=True,
        null=True
    )
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# --------- Tool Model ---------
class Tool(models.Model):
    internal_number = models.CharField(max_length=100, primary_key=True, unique=True, blank=True, db_index=True)  # Add db_index
    serial_number =models.CharField(max_length=100, unique=True, blank=True, null=True, db_index=True)  # Add db_index  
    tool_name = models.CharField(max_length=100, choices = [
    ('radman', 'radman'),
    ('ladsaf', 'ladsaf'),
    ('harness', 'harness'),
    ('pole strap', 'pole strap'),
    ('double lanyard', 'double lanyard'),
    ('triple action carabiner', 'triple action carabiner'),
    ('tools lanyard', 'tools lanyard'),
    ('bag for harness and rigging gears', 'bag for harness and rigging gears'),
    ('helmet for rigger', 'helmet for rigger'),
    ('gloves', 'gloves'),
    ('glasses', 'glasses'),
    ('rescue kit', 'rescue kit'),
    ('spills kit', 'spills kit'),
    ('fire blanket', 'fire blanket'),
    ('slings length and capacity yellow', 'slings length and capacity yellow'),
    ('slings length and capacity green', 'slings length and capacity green'),
    ('first aid kit - survival work place', 'first aid kit - survival work place'),
    ('fire extinguisher 4.5 kg abe dry powder', 'fire extinguisher 4.5 kg abe dry powder'),
    ('cable tie gun', 'cable tie gun'),
    ('tools bag', 'tools bag'),
    ('screwdrivers set', 'screwdrivers set'),
    ('insulated screwdriver 6pcs', 'insulated screwdriver 6pcs'),
    ('allen key (big set)', 'allen key (big set)'),
    ('alan key set star', 'alan key set star'),
    ('ratchet podger 32,30,19', 'ratchet podger 32,30,19'),
    ('adjustable wrench small', 'adjustable wrench small'),
    ('adjustable wrench medium', 'adjustable wrench medium'),
    ('adjustable wrench large', 'adjustable wrench large'),
    ('adjustable wrench xlarge', 'adjustable wrench xlarge'),
    ('stuppy set', 'stuppy set'),
    ('spanner set', 'spanner set'),
    ('reverse combination wrench set', 'reverse combination wrench set'),
    ('drive socket set', 'drive socket set'),
    ('3 piece plier set', '3 piece plier set'),
    ('cable cutter for edge small', 'cable cutter for edge small'),
    ('cable cutter for edge medium', 'cable cutter for edge medium'),
    ('cable cutter large 20 cm to 25 cm', 'cable cutter large 20 cm to 25 cm'),
    ('cable cutter yellow xlarge', 'cable cutter yellow xlarge'),
    ('irwin snips', 'irwin snips'),
    ('cordless hammer drill', 'cordless hammer drill'),
    ('cordless drill', 'cordless drill'),
    ('cordless impact wrench', 'cordless impact wrench'),
    ('cordless driver', 'cordless driver'),
    ('cordless grinder', 'cordless grinder'),
    ('charger makita', 'charger makita'),
    ('battery makita', 'battery makita'),
    ('impact drive socket set', 'impact drive socket set'),
    ('1/4", 3/8" & 1/2" impact socket adaptor set', '1/4", 3/8" & 1/2" impact socket adaptor set'),
    ('sutton hole saw kit', 'sutton hole saw kit'),
    ('steel drill bits set', 'steel drill bits set'),
    ('masonry bits set', 'masonry bits set'),
    ('drill bit set 246', 'drill bit set 246'),
    ('screwdrivers & socket bits set', 'screwdrivers & socket bits set'),
    ('hammer', 'hammer'),
    ('rj45 crimper', 'rj45 crimper'),
    ('hot air gun', 'hot air gun'),
    ('digital level', 'digital level'),
    ('water level', 'water level'),
    ('tape measure', 'tape measure'),
    ('meter tape - laser', 'meter tape - laser'),
    ('rivet gun', 'rivet gun'),
    ('multimeter digital aaa or aa', 'multimeter digital aaa or aa'),
    ('silicon gun', 'silicon gun'),
    ('small lugs crimper size 1 small', 'small lugs crimper size 1 small'),
    ('small lugs crimper size 2 medium', 'small lugs crimper size 2 medium'),
    ('big lugs crimper size 3 large', 'big lugs crimper size 3 large'),
    ('big lugs crimper hydraulic size 4 xlarge', 'big lugs crimper hydraulic size 4 xlarge'),
    ('rcd', 'rcd'),
    ('power lead (20 meters)', 'power lead (20 meters)'),
    ('shovel', 'shovel'),
    ('heavy duty wrecking bar', 'heavy duty wrecking bar'),
    ('jma antenna torque wrench', 'jma antenna torque wrench'),
    ('ladder fibre glass 3m', 'ladder fibre glass 3m'),
    ('filler', 'filler'),
    ('heat gun gas', 'heat gun gas'),
    ('heat gun electrical', 'heat gun electrical'),
    ('ratchets spanner set', 'ratchets spanner set'),
    ('generator', 'generator'),
    ('rain coats', 'rain coats'),
    ('cones 700mm', 'cones 700mm'),
    ('yellow hazard tape', 'yellow hazard tape'),
    ('workers ahead sign', 'workers ahead sign'),
    ('pedestrian sign', 'pedestrian sign'),
    ('tent', 'tent'),
    ('vacuum', 'vacuum'),
    ('brady label printer', 'brady label printer'),
    ('chain block', 'chain block'),
    ('lever block come along', 'lever block come along'),
    ('rope 100 to meters', 'rope 100 to meters'),
    ('otdr + charger + bag + port protector', 'otdr + charger + bag + port protector'),
    ('launch cable', 'launch cable'),
    ('power meter', 'power meter'),
    ('light source', 'light source'),
    ('traffic identifier', 'traffic identifier'),
    ('microscope electronic', 'microscope electronic'),
    ('laser pen 30mw', 'laser pen 30mw'),
    ('cleaner 2.5mm pen', 'cleaner 2.5mm pen'),
    ('cleaner 1.25mm pen', 'cleaner 1.25mm pen'),
    ('cleaner cassette', 'cleaner cassette'),
    ('pon meter', 'pon meter'),
    ('splicer single', 'splicer single'),
    ('cleaver', 'cleaver'),
    ('stripper yellow', 'stripper yellow'),
    ('small blue jacket remover', 'small blue jacket remover'),
    ('big blue jacket remover', 'big blue jacket remover'),
    ('seal breaker', 'seal breaker'),
    ('manhole guards', 'manhole guards'),
    ('pit keys', 'pit keys'),
    ('gas tester with charger + probe (set of 2 devices)', 'gas tester with charger + probe (set of 2 devices)'),
    ('alcohol dispenser', 'alcohol dispenser'),
    ('scissors', 'scissors'),
    ('g jacket remover', 'g jacket remover'),
    ('tpg fist joint holder', 'tpg fist joint holder'),
    ('t jacket remover', 't jacket remover'),
    ('opti tab cable', 'opti tab cable'),
    ('rodder 6mm', 'rodder 6mm'),
    ('rodder 11mm', 'rodder 11mm'),
    ('snake', 'snake'),
    ('printer a4 with usb cable', 'printer a4 with usb cable'),
    ('laptop', 'laptop'),
    ('all data cables needed for projects', 'all data cables needed for projects'),
    ('dymo label printer small', 'dymo label printer small'),
    ('label printer for feeder', 'label printer for feeder'),
    ('dymo embossing rhino heavy duty tool kit m1011', 'dymo embossing rhino heavy duty tool kit m1011'),
    ('laminator', 'laminator'),
    ('wire tracker', 'wire tracker'),
    ('ethernet tester', 'ethernet tester'),
    ('cat5/6 puncher', 'cat5/6 puncher'),
    ('multimeter', 'multimeter'),
]
, db_index=True)  # Add db_index
    brand = models.CharField(max_length=100, default='Generic Brand')
    description = models.TextField(blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    calibration_date = models.DateField(null=True, blank=True)  # Newly Added Field
    store = models.CharField(
        max_length=50,
        choices=[
            ('Online', 'Online'),
            ('Bunnings', 'Bunnings'),
            ('other local stores', 'other local stores')
        ]
    )
    state = models.CharField(
        max_length=50,
        choices=[
            ('NSW', 'NSW'),
            ('VIC', 'VIC'),
            ('WA', 'WA'),
            ('SA', 'SA'),
            ('QLD', 'QLD'),
            ('TZ', 'TZ')
        ]
    )
    quantity = models.PositiveIntegerField(default=1)
    photo = models.ImageField(upload_to='tool_photos/', blank=True, null=True)  # New field for photo
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # New field for cost
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tools')
    assigned_car = models.ForeignKey('Car', on_delete=models.SET_NULL, null=True, blank=True, related_name='tools')

    def __str__(self):
        return f"{self.tool_name} - {self.internal_number}"
# Automatically Assign Default Serial Number if Empty
@receiver(pre_save, sender=Tool)
def add_default_internal_number(sender, instance, **kwargs):
    if not instance.internal_number:
        last_tool = Tool.objects.filter(internal_number__startswith='KE-').order_by('-internal_number').first()
        if last_tool and last_tool.internal_number.startswith('KE-'):
            try:
                last_number = int(last_tool.internal_number.replace('KE-', '') or 0)
                instance.internal_number = f"KE-{last_number + 1}"
            except ValueError:
                instance.internal_number = "KE-01"
        else:
            instance.internal_number = "KE-01"
# --------- Car Model ---------
class Car(models.Model):
    STATE_CHOICES = [('NSW', 'NSW'), ('VIC', 'VIC'), ('WA', 'WA'), ('SA', 'SA'), ('QLD', 'QLD'), ('TZ', 'TZ')]
    BODY_CHOICES = [
        ('Sedan', 'Sedan'),
        ('Hatchback', 'Hatchback'),
        ('SUV', 'SUV'),
        ('Ute', 'Ute'),
        ('Van', 'Van'),
        ('Truck', 'Truck'),
        ('EWP', 'EWP'),
        ('trailer', 'trailer'),
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

    def __str__(self):
        return f"{self.make} {self.model} ({self.rego})"


# --------- Maintenance Model ---------
class Maintenance(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='maintenance_records', db_index=True)  # Add db_index
    tires_change_date = models.DateField()
    tires_alert_km = models.PositiveIntegerField(default=70)
    last_service_date = models.DateField()
    service_alert_km = models.PositiveIntegerField(default=9500)
    mechanic_notes = models.TextField(blank=True)
    tire_alignment = models.BooleanField(default=False)
    tire_status = models.JSONField(default=dict)  # {'tire1': 'Good', 'tire2': 'Worn'}
    monthly_odometer_alert = models.BooleanField(default=True)
    maintenance_actions = models.TextField()  # Line-by-line breakdown
    yearly_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    accident_history = models.TextField(blank=True)

    def __str__(self):
        return f"Maintenance for {self.car.rego}"

# --------- MaintenanceItem Model ---------
class MaintenanceItem(models.Model):
    maintenance = models.ForeignKey('Maintenance', on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.description} - ${self.cost}"
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
