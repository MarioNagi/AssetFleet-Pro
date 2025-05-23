# Generated by Django 5.0.6 on 2025-03-11 23:36

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Car",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("rego", models.CharField(db_index=True, max_length=20, unique=True)),
                ("rego_expiry_date", models.DateField()),
                ("purchase_date", models.DateField(blank=True, null=True)),
                (
                    "purchase_price",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("NSW", "NSW"),
                            ("VIC", "VIC"),
                            ("WA", "WA"),
                            ("SA", "SA"),
                            ("QLD", "QLD"),
                            ("TZ", "TZ"),
                        ],
                        db_index=True,
                        default="NSW",
                        max_length=10,
                    ),
                ),
                ("maintenance_sticker_date", models.DateField()),
                ("make", models.CharField(max_length=100)),
                ("model", models.CharField(max_length=100)),
                ("vin_number", models.CharField(max_length=100, unique=True)),
                (
                    "photo",
                    models.ImageField(blank=True, null=True, upload_to="car_photos/"),
                ),
                (
                    "assigned_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="cars",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Maintenance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tires_change_date", models.DateField()),
                ("tires_alert_km", models.PositiveIntegerField(default=70)),
                ("last_service_date", models.DateField()),
                ("service_alert_km", models.PositiveIntegerField(default=9500)),
                ("mechanic_notes", models.TextField(blank=True)),
                ("tire_alignment", models.BooleanField(default=False)),
                ("tire_status", models.JSONField(default=dict)),
                ("monthly_odometer_alert", models.BooleanField(default=True)),
                ("maintenance_actions", models.TextField()),
                (
                    "yearly_cost",
                    models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
                ),
                ("accident_history", models.TextField(blank=True)),
                (
                    "car",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="maintenance_records",
                        to="tracking.car",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="MaintenanceItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("description", models.CharField(max_length=255)),
                ("cost", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "maintenance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="tracking.maintenance",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="OdometerReading",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("reading_date", models.DateField(default=django.utils.timezone.now)),
                ("reading_value", models.PositiveIntegerField()),
                (
                    "car",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="odometer_readings",
                        to="tracking.car",
                    ),
                ),
            ],
            options={
                "ordering": ["-reading_date"],
            },
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "access_level",
                    models.CharField(
                        choices=[
                            ("User", "User"),
                            ("Manager", "Manager"),
                            ("Admin", "Admin"),
                        ],
                        default="User",
                        max_length=10,
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("NSW", "NSW"),
                            ("VIC", "VIC"),
                            ("WA", "WA"),
                            ("SA", "SA"),
                            ("QLD", "QLD"),
                            ("TZ", "TZ"),
                        ],
                        max_length=10,
                        null=True,
                    ),
                ),
                (
                    "photo",
                    models.ImageField(blank=True, null=True, upload_to="user_photos/"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tool",
            fields=[
                (
                    "internal_number",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=100,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                (
                    "serial_number",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=100,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "tool_name",
                    models.CharField(
                        choices=[
                            ("radman", "radman"),
                            ("ladsaf", "ladsaf"),
                            ("harness", "harness"),
                            ("pole strap", "pole strap"),
                            ("double lanyard", "double lanyard"),
                            ("triple action carabiner", "triple action carabiner"),
                            ("tools lanyard", "tools lanyard"),
                            (
                                "bag for harness and rigging gears",
                                "bag for harness and rigging gears",
                            ),
                            ("helmet for rigger", "helmet for rigger"),
                            ("gloves", "gloves"),
                            ("glasses", "glasses"),
                            ("rescue kit", "rescue kit"),
                            ("spills kit", "spills kit"),
                            ("fire blanket", "fire blanket"),
                            (
                                "slings length and capacity yellow",
                                "slings length and capacity yellow",
                            ),
                            (
                                "slings length and capacity green",
                                "slings length and capacity green",
                            ),
                            (
                                "first aid kit - survival work place",
                                "first aid kit - survival work place",
                            ),
                            (
                                "fire extinguisher 4.5 kg abe dry powder",
                                "fire extinguisher 4.5 kg abe dry powder",
                            ),
                            ("cable tie gun", "cable tie gun"),
                            ("tools bag", "tools bag"),
                            ("screwdrivers set", "screwdrivers set"),
                            (
                                "insulated screwdriver 6pcs",
                                "insulated screwdriver 6pcs",
                            ),
                            ("allen key (big set)", "allen key (big set)"),
                            ("alan key set star", "alan key set star"),
                            ("ratchet podger 32,30,19", "ratchet podger 32,30,19"),
                            ("adjustable wrench small", "adjustable wrench small"),
                            ("adjustable wrench medium", "adjustable wrench medium"),
                            ("adjustable wrench large", "adjustable wrench large"),
                            ("adjustable wrench xlarge", "adjustable wrench xlarge"),
                            ("stuppy set", "stuppy set"),
                            ("spanner set", "spanner set"),
                            (
                                "reverse combination wrench set",
                                "reverse combination wrench set",
                            ),
                            ("drive socket set", "drive socket set"),
                            ("3 piece plier set", "3 piece plier set"),
                            (
                                "cable cutter for edge small",
                                "cable cutter for edge small",
                            ),
                            (
                                "cable cutter for edge medium",
                                "cable cutter for edge medium",
                            ),
                            (
                                "cable cutter large 20 cm to 25 cm",
                                "cable cutter large 20 cm to 25 cm",
                            ),
                            (
                                "cable cutter yellow xlarge",
                                "cable cutter yellow xlarge",
                            ),
                            ("irwin snips", "irwin snips"),
                            ("cordless hammer drill", "cordless hammer drill"),
                            ("cordless drill", "cordless drill"),
                            ("cordless impact wrench", "cordless impact wrench"),
                            ("cordless driver", "cordless driver"),
                            ("cordless grinder", "cordless grinder"),
                            ("charger makita", "charger makita"),
                            ("battery makita", "battery makita"),
                            ("impact drive socket set", "impact drive socket set"),
                            (
                                '1/4", 3/8" & 1/2" impact socket adaptor set',
                                '1/4", 3/8" & 1/2" impact socket adaptor set',
                            ),
                            ("sutton hole saw kit", "sutton hole saw kit"),
                            ("steel drill bits set", "steel drill bits set"),
                            ("masonry bits set", "masonry bits set"),
                            ("drill bit set 246", "drill bit set 246"),
                            (
                                "screwdrivers & socket bits set",
                                "screwdrivers & socket bits set",
                            ),
                            ("hammer", "hammer"),
                            ("rj45 crimper", "rj45 crimper"),
                            ("hot air gun", "hot air gun"),
                            ("digital level", "digital level"),
                            ("water level", "water level"),
                            ("tape measure", "tape measure"),
                            ("meter tape - laser", "meter tape - laser"),
                            ("rivet gun", "rivet gun"),
                            (
                                "multimeter digital aaa or aa",
                                "multimeter digital aaa or aa",
                            ),
                            ("silicon gun", "silicon gun"),
                            (
                                "small lugs crimper size 1 small",
                                "small lugs crimper size 1 small",
                            ),
                            (
                                "small lugs crimper size 2 medium",
                                "small lugs crimper size 2 medium",
                            ),
                            (
                                "big lugs crimper size 3 large",
                                "big lugs crimper size 3 large",
                            ),
                            (
                                "big lugs crimper hydraulic size 4 xlarge",
                                "big lugs crimper hydraulic size 4 xlarge",
                            ),
                            ("rcd", "rcd"),
                            ("power lead (20 meters)", "power lead (20 meters)"),
                            ("shovel", "shovel"),
                            ("heavy duty wrecking bar", "heavy duty wrecking bar"),
                            ("jma antenna torque wrench", "jma antenna torque wrench"),
                            ("ladder fibre glass 3m", "ladder fibre glass 3m"),
                            ("filler", "filler"),
                            ("heat gun gas", "heat gun gas"),
                            ("heat gun electrical", "heat gun electrical"),
                            ("ratchets spanner set", "ratchets spanner set"),
                            ("generator", "generator"),
                            ("rain coats", "rain coats"),
                            ("cones 700mm", "cones 700mm"),
                            ("yellow hazard tape", "yellow hazard tape"),
                            ("workers ahead sign", "workers ahead sign"),
                            ("pedestrian sign", "pedestrian sign"),
                            ("tent", "tent"),
                            ("vacuum", "vacuum"),
                            ("brady label printer", "brady label printer"),
                            ("chain block", "chain block"),
                            ("lever block come along", "lever block come along"),
                            ("rope 100 to meters", "rope 100 to meters"),
                            (
                                "otdr + charger + bag + port protector",
                                "otdr + charger + bag + port protector",
                            ),
                            ("launch cable", "launch cable"),
                            ("power meter", "power meter"),
                            ("light source", "light source"),
                            ("traffic identifier", "traffic identifier"),
                            ("microscope electronic", "microscope electronic"),
                            ("laser pen 30mw", "laser pen 30mw"),
                            ("cleaner 2.5mm pen", "cleaner 2.5mm pen"),
                            ("cleaner 1.25mm pen", "cleaner 1.25mm pen"),
                            ("cleaner cassette", "cleaner cassette"),
                            ("pon meter", "pon meter"),
                            ("splicer single", "splicer single"),
                            ("cleaver", "cleaver"),
                            ("stripper yellow", "stripper yellow"),
                            ("small blue jacket remover", "small blue jacket remover"),
                            ("big blue jacket remover", "big blue jacket remover"),
                            ("seal breaker", "seal breaker"),
                            ("manhole guards", "manhole guards"),
                            ("pit keys", "pit keys"),
                            (
                                "gas tester with charger + probe (set of 2 devices)",
                                "gas tester with charger + probe (set of 2 devices)",
                            ),
                            ("alcohol dispenser", "alcohol dispenser"),
                            ("scissors", "scissors"),
                            ("g jacket remover", "g jacket remover"),
                            ("tpg fist joint holder", "tpg fist joint holder"),
                            ("t jacket remover", "t jacket remover"),
                            ("opti tab cable", "opti tab cable"),
                            ("rodder 6mm", "rodder 6mm"),
                            ("rodder 11mm", "rodder 11mm"),
                            ("snake", "snake"),
                            ("printer a4 with usb cable", "printer a4 with usb cable"),
                            ("laptop", "laptop"),
                            (
                                "all data cables needed for projects",
                                "all data cables needed for projects",
                            ),
                            ("dymo label printer small", "dymo label printer small"),
                            ("label printer for feeder", "label printer for feeder"),
                            (
                                "dymo embossing rhino heavy duty tool kit m1011",
                                "dymo embossing rhino heavy duty tool kit m1011",
                            ),
                            ("laminator", "laminator"),
                            ("wire tracker", "wire tracker"),
                            ("ethernet tester", "ethernet tester"),
                            ("cat5/6 puncher", "cat5/6 puncher"),
                            ("multimeter", "multimeter"),
                        ],
                        db_index=True,
                        max_length=100,
                    ),
                ),
                ("brand", models.CharField(default="Generic Brand", max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                ("size", models.CharField(blank=True, max_length=50, null=True)),
                ("calibration_date", models.DateField(blank=True, null=True)),
                (
                    "store",
                    models.CharField(
                        choices=[
                            ("Online", "Online"),
                            ("Bunnings", "Bunnings"),
                            ("other local stores", "other local stores"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("NSW", "NSW"),
                            ("VIC", "VIC"),
                            ("WA", "WA"),
                            ("SA", "SA"),
                            ("QLD", "QLD"),
                            ("TZ", "TZ"),
                        ],
                        max_length=50,
                    ),
                ),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "assigned_car",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tools",
                        to="tracking.car",
                    ),
                ),
                (
                    "assigned_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tools",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Transfer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "transfer_type",
                    models.CharField(
                        choices=[("Tool", "Tool"), ("Car", "Car")], max_length=10
                    ),
                ),
                ("item_id", models.PositiveIntegerField()),
                (
                    "date_of_transfer",
                    models.DateField(default=django.utils.timezone.now),
                ),
                (
                    "from_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="transfers_from",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "to_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="transfers_to",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
