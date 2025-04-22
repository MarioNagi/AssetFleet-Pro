from django.contrib import admin
from .models import Profile, Tool, Car, OdometerReading, Maintenance, Transfer
from django.utils.html import format_html


# --------- Profile Admin ---------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'access_level', 'state', 'display_photo')
    list_filter = ('access_level', 'state')
    search_fields = ('user__username', 'user__email')

    def display_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" />', obj.photo.url)
        return "No Photo"
    display_photo.short_description = 'Photo'


# --------- Tool Admin ---------
@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('tool_name', 'brand', 'description', 'size', 'store', 'state', 'quantity', 'assigned_user')
    list_filter = ('tool_name', 'brand', 'state', 'assigned_user')
    search_fields = ('tool_name', 'brand', 'assigned_user__username')


# --------- Car Admin ---------
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        'rego', 'make', 'model', 'state', 'purchase_date', 'purchase_price',
        'assigned_user', 'rego_expiry_date', 'maintenance_sticker_date', 'is_rego_due', 'is_maintenance_due'
    )
    list_filter = ('make', 'model', 'state', 'assigned_user')
    search_fields = ('rego', 'vin_number', 'make', 'model')

    def is_rego_due(self, obj):
        return obj.is_rego_due()
    is_rego_due.boolean = True
    is_rego_due.short_description = 'Rego Due'

    def is_maintenance_due(self, obj):
        return obj.is_maintenance_due()
    is_maintenance_due.boolean = True
    is_maintenance_due.short_description = 'Maintenance Due'


# --------- Maintenance Admin ---------
@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = (
        'car', 'tires_change_date', 'last_service_date', 'tire_alignment',
        'yearly_cost', 'monthly_odometer_alert'
    )
    list_filter = ('car', 'tires_change_date', 'last_service_date', 'tire_alignment')
    search_fields = ('car__rego', 'mechanic_notes')


# --------- Odometer Reading Admin ---------
@admin.register(OdometerReading)
class OdometerReadingAdmin(admin.ModelAdmin):
    list_display = ('car', 'reading_date', 'reading_value')
    list_filter = ('car', 'reading_date')
    search_fields = ('car__rego',)


# --------- Transfer Admin ---------
@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('transfer_type', 'item_id', 'from_user', 'to_user', 'date_of_transfer')
    list_filter = ('transfer_type', 'date_of_transfer')
    search_fields = ('from_user__username', 'to_user__username')
