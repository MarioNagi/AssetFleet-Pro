import csv
import xlsxwriter
import json
from django.http import HttpResponse, JsonResponse
from django.db import connections
from redis import Redis
from django.conf import settings
import datetime
from datetime import timedelta
import logging
from django.utils import timezone
import re
from django.db.models import Max
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.contrib.auth.views import LoginView
from .mixins import UserRequiredMixin, ManagerRequiredMixin, AdminRequiredMixin, AdminManagerRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Tool, Car, Transfer, OdometerReading, Maintenance
from .forms import (
    ToolForm, CarForm, TransferForm, OdometerReadingForm, 
    MaintenanceForm, ImportForm, UserUpdateForm, MaintenanceItemFormSet
)

logger = logging.getLogger(__name__)

class DashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        access_level = request.user.profile.access_level.lower()
        if access_level == 'admin':
            return redirect('admin_dashboard')
        elif access_level == 'manager':
            return redirect('manager_dashboard')
        else:  # User level
            return redirect('user_dashboard')

# ----- Login View -----
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.profile.access_level.lower() == 'admin':
            return reverse_lazy('admin_dashboard')
        elif user.profile.access_level.lower() == 'manager':
            return reverse_lazy('manager_dashboard')
        else:
            return reverse_lazy('user_dashboard')

# ----- Dashboard Views -----
class AdminDashboardView(AdminRequiredMixin, TemplateView):
    template_name = 'tracking/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tools'] = Tool.objects.all()
        context['cars'] = Car.objects.all()
        context['users'] = User.objects.all()
        context["maintenance_records"] = Maintenance.objects.all()
        return context

class ManagerDashboardView(ManagerRequiredMixin, TemplateView):
    template_name = 'tracking/manager_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_state = self.request.user.profile.state
        context['tools'] = Tool.objects.filter(state=user_state)
        context['cars'] = Car.objects.filter(state=user_state)
        return context

class UserDashboardView(UserRequiredMixin, TemplateView):
    template_name = 'tracking/user_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cars'] = Car.objects.filter(assigned_user=self.request.user)
        return context

# ----- Role-Specific Car Views -----
class UserCarView(UserRequiredMixin, ListView):
    model = Car
    template_name = 'tracking/user_car_list.html'
    context_object_name = 'cars'

    def get_queryset(self):
        return Car.objects.filter(assigned_user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['odometer_readings'] = OdometerReading.objects.filter(
            car__assigned_user=self.request.user
        ).order_by('-reading_date')[:5]
        return context

class AdminCarView(AdminRequiredMixin, ListView):
    model = Car
    template_name = 'tracking/car_list.html'
    context_object_name = 'cars'

    def get_queryset(self):
        return Car.objects.all()

# ----- Manager-Specific Views -----
class ManagerToolListView(ManagerRequiredMixin, ListView):
    model = Tool
    template_name = 'tracking/manager_tool_list.html'
    context_object_name = 'tools'

    def get_queryset(self):
        user = self.request.user
        if user.profile.access_level.lower() == 'manager':
            return Tool.objects.filter(state=user.profile.state)
        return Tool.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['state'] = self.request.user.profile.state
        return context

class ManagerCarListView(ManagerRequiredMixin, ListView):
    model = Car
    template_name = 'tracking/manager_car_list.html'
    context_object_name = 'cars'

    def get_queryset(self):
        user = self.request.user
        if user.profile.access_level.lower() == 'manager':
            return Car.objects.filter(state=user.profile.state)
        return Car.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['state'] = self.request.user.profile.state
        return context

# ----- Tool Views -----
class ToolListView(LoginRequiredMixin, ListView):
    model = Tool
    template_name = 'tracking/tool_list.html'
    context_object_name = 'tools'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().select_related('assigned_user', 'assigned_car')
        
        # Apply filters
        user_filter = self.request.GET.get('user')
        tool_name_filter = self.request.GET.get('tool_name')
        state_filter = self.request.GET.get('state')
        brand_filter = self.request.GET.get('brand')
        car_filter = self.request.GET.get('car')

        if user_filter:
            queryset = queryset.filter(assigned_user_id=user_filter)
        if tool_name_filter:
            queryset = queryset.filter(tool_name=tool_name_filter)
        if state_filter:
            queryset = queryset.filter(state=state_filter)
        if brand_filter:
            queryset = queryset.filter(brand=brand_filter)
        if car_filter:
            queryset = queryset.filter(assigned_car__rego=car_filter)
        
        # Apply user-level filtering
        if user.profile.access_level.lower() == 'admin':
            return queryset
        elif user.profile.access_level.lower() == 'manager':
            return queryset.filter(state=user.profile.state)
        else:  # User level
            return queryset.filter(assigned_user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get available users based on access level
        if user.profile.access_level.lower() == 'admin':
            context['users'] = User.objects.all()
        elif user.profile.access_level.lower() == 'manager':
            context['users'] = User.objects.filter(profile__state=user.profile.state)
        else:
            context['users'] = User.objects.filter(id=user.id)

        # Get unique values for filter dropdowns
        all_tools = self.model.objects.all()
        context['tool_names'] = all_tools.values_list('tool_name', flat=True).distinct()
        context['states'] = all_tools.values_list('state', flat=True).distinct()
        context['brands'] = all_tools.values_list('brand', flat=True).distinct()
        context['cars'] = Car.objects.values('rego').distinct()
        
        return context

class ToolCreateView(LoginRequiredMixin, CreateView):
    model = Tool
    form_class = ToolForm
    template_name = 'tracking/tool_form.html'
    success_url = reverse_lazy('tool_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if user.profile.access_level.lower() != 'admin':
            form.fields['state'].initial = user.profile.state
            form.fields['state'].disabled = True
        return form

class ToolUpdateView(LoginRequiredMixin, UpdateView):
    model = Tool
    form_class = ToolForm
    template_name = 'tracking/tool_form.html'
    success_url = reverse_lazy('tool_list')

    def get_queryset(self):
        user = self.request.user
        if user.profile.access_level.lower() == 'admin':
            return super().get_queryset()
        return super().get_queryset().filter(state=user.profile.state)

class ToolDeleteView(LoginRequiredMixin, DeleteView):
    model = Tool
    template_name = 'tracking/tool_confirm_delete.html'
    success_url = reverse_lazy('tool_list')

# ----- Car Views -----
class CarListView(LoginRequiredMixin, ListView):
    model = Car
    template_name = 'tracking/car_list.html'
    context_object_name = 'cars'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().select_related('assigned_user')
        
        # Apply filters
        rego = self.request.GET.get('rego')
        year = self.request.GET.get('year')
        rego_expiry = self.request.GET.get('rego_expiry')
        
        if rego:
            queryset = queryset.filter(rego__icontains=rego)
        if year:
            queryset = queryset.filter(manufacturing_year=year)
        if rego_expiry:
            queryset = queryset.filter(rego_expiry_date__year=rego_expiry)
        
        # Apply user-level filtering
        if user.profile.access_level.lower() == 'admin':
            return queryset
        elif user.profile.access_level.lower() == 'manager':
            return queryset.filter(state=user.profile.state)
        else:  # User level
            return queryset.filter(assigned_user=user)
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get unique values for filter dropdowns
        all_cars = self.model.objects.all()
        context['regos'] = all_cars.values_list('rego', flat=True).distinct()
        context['years'] = all_cars.values_list('manufacturing_year', flat=True).distinct()
        context['rego_expiry_years'] = all_cars.dates('rego_expiry_date', 'year')
        return context

class CarCreateView(LoginRequiredMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = 'tracking/car_form.html'
    success_url = reverse_lazy('car_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if user.profile.access_level.lower() != 'admin':
            form.fields['state'].initial = user.profile.state
            form.fields['state'].disabled = True
            form.fields['assigned_user'].queryset = User.objects.filter(
                profile__state=user.profile.state
            )
        return form

class CarUpdateView(LoginRequiredMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'tracking/car_form.html'
    success_url = reverse_lazy('car_list')

    def get_queryset(self):
        user = self.request.user
        if user.profile.access_level.lower() == 'admin':
            return super().get_queryset()
        return super().get_queryset().filter(state=user.profile.state)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if user.profile.access_level.lower() != 'admin':
            form.fields['state'].disabled = True
            form.fields['assigned_user'].queryset = User.objects.filter(
                profile__state=user.profile.state
            )
        return form

class CarDeleteView(LoginRequiredMixin, DeleteView):
    model = Car
    template_name = 'tracking/car_confirm_delete.html'
    success_url = reverse_lazy('car_list')

# ----- Odometer Reading Views -----
class OdometerReadingListView(LoginRequiredMixin, ListView):
    model = OdometerReading
    template_name = 'tracking/odometer_list.html'
    context_object_name = 'odometer_readings'
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().select_related('car')
        
        if user.profile.access_level.lower() == 'admin':
            return queryset
        elif user.profile.access_level.lower() == 'manager':
            return queryset.filter(car__state=user.profile.state)
        else:  # User level
            return queryset.filter(car__assigned_user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.profile.access_level.lower() == 'admin':
            context['cars'] = Car.objects.all()
        elif user.profile.access_level.lower() == 'manager':
            context['cars'] = Car.objects.filter(state=user.profile.state)
        else:
            context['cars'] = Car.objects.filter(assigned_user=user)
        return context

class OdometerReadingCreateView(UserRequiredMixin, CreateView):
    model = OdometerReading
    form_class = OdometerReadingForm
    template_name = 'tracking/odometer_form.html'
    success_url = reverse_lazy('odometer_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if user.profile.access_level.lower() == 'admin':
            form.fields['car'].queryset = Car.objects.all()
        elif user.profile.access_level.lower() == 'manager':
            form.fields['car'].queryset = Car.objects.filter(state=user.profile.state)
        else:
            form.fields['car'].queryset = Car.objects.filter(assigned_user=user)
        return form

class OdometerReadingUpdateView(LoginRequiredMixin, UpdateView):
    model = OdometerReading
    form_class = OdometerReadingForm
    template_name = 'tracking/odometer_form.html'
    success_url = reverse_lazy('odometer_list')

    def get_queryset(self):
        user = self.request.user
        if user.profile.access_level.lower() == 'admin':
            return super().get_queryset()
        return super().get_queryset().filter(car__state=user.profile.state)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if user.profile.access_level.lower() == 'admin':
            form.fields['car'].queryset = Car.objects.all()
        elif user.profile.access_level.lower() == 'manager':
            form.fields['car'].queryset = Car.objects.filter(state=user.profile.state)
        return form

class OdometerReadingDeleteView(AdminRequiredMixin, DeleteView):
    model = OdometerReading
    template_name = 'tracking/odometer_confirm_delete.html'
    success_url = reverse_lazy('odometer_list')

# ----- Maintenance Views -----
class MaintenanceRecordListView(LoginRequiredMixin, ListView):
    model = Maintenance
    template_name = 'tracking/maintenance_list.html'
    context_object_name = 'maintenance_records'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('car')
        user = self.request.user
        
        # Apply rego filter
        rego = self.request.GET.get('rego')
        if rego:
            queryset = queryset.filter(car__rego__icontains=rego)
        
        # Apply user-level filtering
        if user.profile.access_level.lower() == 'admin':
            return queryset
        elif user.profile.access_level.lower() == 'manager':
            return queryset.filter(car__state=user.profile.state)
        else:  # User level
            return queryset.filter(car__assigned_user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get unique regos for filter dropdown
        context['regos'] = Car.objects.values_list('rego', flat=True).distinct()
        return context

class MaintenanceRecordCreateView(LoginRequiredMixin, CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'tracking/maintenance_form.html'
    success_url = reverse_lazy('maintenance_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['item_formset'] = MaintenanceItemFormSet(self.request.POST)
        else:
            context['item_formset'] = MaintenanceItemFormSet()
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if user.profile.access_level.lower() == 'admin':
            form.fields['car'].queryset = Car.objects.all()
        else:
            form.fields['car'].queryset = Car.objects.filter(state=user.profile.state)
        return form

    def form_valid(self, form):
        context = self.get_context_data()
        item_formset = context['item_formset']
        if form.is_valid() and item_formset.is_valid():
            maintenance = form.save()
            items = item_formset.save(commit=False)
            for item in items:
                item.maintenance = maintenance
                item.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))

class MaintenanceRecordUpdateView(LoginRequiredMixin, UpdateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'tracking/maintenance_form.html'
    success_url = reverse_lazy('maintenance_list')

    def get_queryset(self):
        user = self.request.user
        if user.profile.access_level.lower() == 'admin':
            return super().get_queryset()
        return super().get_queryset().filter(car__state=user.profile.state)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['item_formset'] = MaintenanceItemFormSet(self.request.POST, instance=self.object)
        else:
            context['item_formset'] = MaintenanceItemFormSet(instance=self.object)
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        if user.profile.access_level.lower() == 'admin':
            form.fields['car'].queryset = Car.objects.all()
        else:
            form.fields['car'].queryset = Car.objects.filter(state=user.profile.state)
        return form

    def form_valid(self, form):
        context = self.get_context_data()
        item_formset = context['item_formset']
        if form.is_valid() and item_formset.is_valid():
            maintenance = form.save()
            items = item_formset.save(commit=False)
            for item in items:
                item.maintenance = maintenance
                item.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))

class MaintenanceRecordDeleteView(AdminRequiredMixin, DeleteView):
    model = Maintenance
    template_name = 'tracking/maintenance_confirm_delete.html'
    success_url = reverse_lazy('maintenance_list')

# ----- Transfer Views -----
class TransferListView(AdminManagerRequiredMixin, ListView):
    model = Transfer
    template_name = 'tracking/transfer_list.html'
    context_object_name = 'transfers'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        if user.profile.access_level.lower() == 'admin':
            return queryset
        else:  # manager
            return queryset.filter(from_user__profile__state=user.profile.state) | \
                   queryset.filter(to_user__profile__state=user.profile.state)

class TransferCreateView(AdminManagerRequiredMixin, CreateView):
    model = Transfer
    form_class = TransferForm
    template_name = 'tracking/transfer_form.html'
    success_url = reverse_lazy('transfer_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        
        # Filter available users based on access level
        if user.profile.access_level.lower() == 'admin':
            form.fields['from_user'].queryset = User.objects.all()
            form.fields['to_user'].queryset = User.objects.all()
        else:  # manager
            state = user.profile.state
            form.fields['from_user'].queryset = User.objects.filter(profile__state=state)
            form.fields['to_user'].queryset = User.objects.filter(profile__state=state)
            
        return form

    def form_valid(self, form):
        try:
            transfer = form.save(commit=False)
            
            # Get the item being transferred
            if transfer.transfer_type == 'Tool':
                item = Tool.objects.get(pk=transfer.item_id)
                if item.assigned_user != transfer.from_user:
                    messages.error(self.request, 'This tool is not assigned to the source user.')
                    return super().form_invalid(form)
                item.assigned_user = transfer.to_user
                item.save()
            else:  # Car transfer
                item = Car.objects.get(pk=transfer.item_id)
                if item.assigned_user != transfer.from_user:
                    messages.error(self.request, 'This car is not assigned to the source user.')
                    return super().form_invalid(form)
                item.assigned_user = transfer.to_user
                item.save()

            transfer.save()
            messages.success(self.request, 'Transfer completed successfully.')
            return super().form_valid(form)
            
        except (Tool.DoesNotExist, Car.DoesNotExist):
            messages.error(self.request, 'The specified item does not exist.')
            return super().form_invalid(form)

# ----- User Management Views -----
class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = 'tracking/user_list.html'
    context_object_name = 'users'

class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'tracking/user_form.html'
    success_url = reverse_lazy('user_list')

class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'tracking/user_form.html'
    success_url = reverse_lazy('user_list')

class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = 'tracking/user_confirm_delete.html'
    success_url = reverse_lazy('user_list')

# ----- Import/Export Views -----
class ImportView(AdminRequiredMixin, FormView):
    form_class = ImportForm
    template_name = 'tracking/import_form.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        file = form.cleaned_data['file']
        import_type = form.cleaned_data['type']
        file_format = form.cleaned_data['format']
        
        try:
            if file_format == 'csv':
                df = pd.read_csv(file)
            else:  # excel
                df = pd.read_excel(file)
            
            # Process based on type
            if import_type == 'User':
                self._process_user_import(df)
            elif import_type == 'Car':
                self._process_car_import(df)
            elif import_type == 'Tool':
                self._process_tool_import(df)
            
            messages.success(self.request, f'Successfully imported {import_type} data')
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, f'Error importing file: {str(e)}')
            return super().form_invalid(form)

    def _process_user_import(self, df):
        required_cols = ['username', 'email', 'first_name', 'last_name', 
                        'password', 'access_level', 'state']
        if not all(col in df.columns for col in required_cols):
            raise ValueError('Missing required columns for user import')
        
        for _, row in df.iterrows():
            user, created = User.objects.update_or_create(
                username=row['username'],
                defaults={
                    'email': row['email'],
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                }
            )
            if created:
                user.set_password(row['password'])
            user.save()

            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'access_level': row['access_level'].upper(),
                    'state': row['state'].upper(),
                }
            )

    def _process_car_import(self, df):
        required_cols = ['rego', 'rego_expiry_date', 'state', 'make', 'model',
                        'vin_number', 'manufacturing_year', 'color', 'body',
                        'assigned_user', 'maintenance_sticker_date']
        if not all(col in df.columns for col in required_cols):
            raise ValueError('Missing required columns for car import')

        for _, row in df.iterrows():
            # Get assigned user
            try:
                assigned_user = User.objects.get(username=row['assigned_user'])
            except User.DoesNotExist:
                messages.warning(self.request, 
                    f"User {row['assigned_user']} not found, skipping car {row['rego']}")
                continue

            # Prepare car data
            car_data = {
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
            optional_fields = ['purchase_date', 'purchase_price', 
                             'service_interval_km', 'last_service_km']
            for field in optional_fields:
                if field in df.columns and pd.notna(row[field]):
                    if field == 'purchase_date':
                        car_data[field] = pd.to_datetime(row[field]).date()
                    else:
                        car_data[field] = row[field]

            Car.objects.update_or_create(
                rego=row['rego'],
                defaults=car_data
            )

    def _process_tool_import(self, df):
        required_cols = ['internal_number', 'tool_name', 'state']
        if not all(col in df.columns for col in required_cols):
            raise ValueError('Missing required columns for tool import')

        for _, row in df.iterrows():
            tool_data = {
                'tool_name': row['tool_name'],
                'state': row['state'].upper(),
            }

            # Handle optional fields
            optional_fields = {
                'serial_number': str,
                'brand': str,
                'description': str,
                'size': str,
                'calibration_date': lambda x: pd.to_datetime(x).date(),
                'store': str,
                'quantity': int,
                'estimated_cost': float
            }

            for field, converter in optional_fields.items():
                if field in df.columns and pd.notna(row[field]):
                    tool_data[field] = converter(row[field])

            # Handle assigned user and car if present
            if 'assigned_user' in df.columns and pd.notna(row['assigned_user']):
                try:
                    tool_data['assigned_user'] = User.objects.get(
                        username=row['assigned_user'])
                except User.DoesNotExist:
                    messages.warning(self.request, 
                        f"User {row['assigned_user']} not found for tool {row['internal_number']}")

            if 'assigned_car' in df.columns and pd.notna(row['assigned_car']):
                try:
                    tool_data['assigned_car'] = Car.objects.get(
                        rego=row['assigned_car'])
                except Car.DoesNotExist:
                    messages.warning(self.request, 
                        f"Car {row['assigned_car']} not found for tool {row['internal_number']}")

# ----- Analytics and Report Views -----
class FleetAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'tracking/fleet_analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        current_year = timezone.now().year
        
        # Filter cars based on access level and rego filter
        if user.profile.access_level.lower() == 'admin':
            cars = Car.objects.all()
        elif user.profile.access_level.lower() == 'manager':
            cars = Car.objects.filter(state=user.profile.state)
        else:
            cars = Car.objects.filter(assigned_user=user)

        # Apply rego filter if provided
        rego = self.request.GET.get('rego')
        if rego:
            cars = cars.filter(rego__icontains=rego)

        # Add regos for filter dropdown
        context['regos'] = Car.objects.values_list('rego', flat=True).distinct()
        context['total_cars'] = cars.count()
        context['cars'] = cars

        # Calculate statistics
        start_of_year = timezone.datetime(current_year, 1, 1)
        ytd_maintenance_cost = sum(car.get_maintenance_costs(start_date=start_of_year)['total_cost'] for car in cars)
        ytd_fuel_cost = sum(car.get_total_costs(start_date=start_of_year)['fuel_cost'] for car in cars)
        
        context['total_maintenance_cost'] = ytd_maintenance_cost
        context['total_fuel_cost'] = ytd_fuel_cost
        context['service_due_cars'] = [car for car in cars if car.is_service_due() or car.is_service_due_by_km()]

        # Monthly costs
        monthly_maintenance_costs = []
        monthly_fuel_costs = []
        for month in range(1, 13):
            month_start = timezone.datetime(current_year, month, 1)
            if month == 12:
                month_end = timezone.datetime(current_year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = timezone.datetime(current_year, month + 1, 1) - timedelta(days=1)

            month_maintenance = sum(car.get_maintenance_costs(
                start_date=month_start,
                end_date=month_end
            )['total_cost'] for car in cars)
            
            month_fuel = sum(car.get_total_costs(
                start_date=month_start,
                end_date=month_end
            )['fuel_cost'] for car in cars)
            
            monthly_maintenance_costs.append(float(month_maintenance))
            monthly_fuel_costs.append(float(month_fuel))

        context['monthly_maintenance_costs'] = json.dumps(monthly_maintenance_costs)
        context['monthly_fuel_costs'] = json.dumps(monthly_fuel_costs)

        # Cost per vehicle data
        vehicle_costs = []
        vehicle_labels = []
        for car in cars:
            total_costs = car.get_total_costs(start_date=start_of_year)
            if total_costs['total_cost'] > 0:
                vehicle_costs.append(float(total_costs['total_cost']))
                vehicle_labels.append(f"{car.rego} ({car.make} {car.model})")
        
        context['vehicle_costs'] = json.dumps(vehicle_costs)
        context['vehicle_labels'] = json.dumps(vehicle_labels)

        # Fuel efficiency analysis
        cars_fuel_data = []
        for car in cars:
            efficiency_data = car.get_fuel_efficiency(last_n_records=5)
            if efficiency_data:
                last_month_start = timezone.now().date().replace(day=1) - timedelta(days=1)
                last_month_start = last_month_start.replace(day=1)
                last_month_end = timezone.now().date().replace(day=1) - timedelta(days=1)
                
                monthly_costs = car.get_total_costs(
                    start_date=last_month_start,
                    end_date=last_month_end
                )
                
                cars_fuel_data.append({
                    'rego': car.rego,
                    'current_efficiency': efficiency_data['current'],
                    'avg_efficiency': efficiency_data['average'],
                    'best_efficiency': efficiency_data['best'],
                    'monthly_fuel_cost': monthly_costs['fuel_cost'],
                    'previous_efficiency': car.get_fuel_efficiency(last_n_records=6)['current']
                })
        
        context['cars_fuel_data'] = cars_fuel_data
        return context

class GenerateReportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Get cars based on user's access level
        if user.profile.access_level.lower() == 'admin':
            cars = Car.objects.all()
        elif user.profile.access_level.lower() == 'manager':
            cars = Car.objects.filter(state=user.profile.state)
        else:
            cars = Car.objects.filter(assigned_user=user)

        report_type = request.GET.get('type', 'excel')
        report_period = request.GET.get('period', 'monthly')
        
        # Calculate date range
        end_date = timezone.now().date()
        if report_period == 'yearly':
            start_date = end_date - timedelta(days=365)
        else:  # monthly
            start_date = end_date - timedelta(days=30)

        # Collect data
        report_data = []
        total_maintenance_cost = 0
        total_fuel_cost = 0

        for car in cars:
            maintenance_records = car.maintenance_records.filter(
                service_date__range=[start_date, end_date]
            )
            maintenance_cost = sum(record.total_cost for record in maintenance_records)
            total_maintenance_cost += maintenance_cost

            fuel_records = car.fuel_records.filter(
                date__range=[start_date, end_date]
            )
            fuel_cost = sum(record.total_cost for record in fuel_records)
            total_fuel_cost += fuel_cost

            last_service = maintenance_records.filter(
                service_type='regular'
            ).order_by('-service_date').first()

            efficiency_data = car.get_fuel_efficiency(last_n_records=5)
            
            report_data.append({
                'rego': car.rego,
                'make_model': f"{car.make} {car.model}",
                'maintenance_cost': maintenance_cost,
                'fuel_cost': fuel_cost,
                'total_cost': maintenance_cost + fuel_cost,
                'last_service': last_service,
                'fuel_efficiency': efficiency_data['current'] if efficiency_data else None
            })

        if report_type == 'excel':
            return self._generate_excel_report(report_data, start_date, end_date,
                                            total_maintenance_cost, total_fuel_cost)
        else:  # csv
            return self._generate_csv_report(report_data, start_date, end_date,
                                           total_maintenance_cost, total_fuel_cost)

    def _generate_excel_report(self, data, start_date, end_date, total_maintenance, total_fuel):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=fleet_report_{start_date.strftime("%Y%m%d")}.xlsx'

        workbook = xlsxwriter.Workbook(response)
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})
        money_format = workbook.add_format({'num_format': '$#,##0.00'})

        # Write headers and summary
        worksheet.write('A1', 'Fleet Cost Report', bold)
        worksheet.write('A2', f'Period: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}')
        worksheet.write('A3', f'Total Maintenance Cost: ${total_maintenance:,.2f}')
        worksheet.write('A4', f'Total Fuel Cost: ${total_fuel:,.2f}')
        worksheet.write('A5', f'Total Fleet Cost: ${(total_maintenance + total_fuel):,.2f}')

        # Write data
        headers = ['Rego', 'Make/Model', 'Maintenance Cost', 'Fuel Cost', 'Total Cost', 'Last Service', 'Fuel Efficiency']
        for col, header in enumerate(headers):
            worksheet.write(6, col, header, bold)

        for row, item in enumerate(data, start=7):
            worksheet.write(row, 0, item['rego'])
            worksheet.write(row, 1, item['make_model'])
            worksheet.write(row, 2, item['maintenance_cost'], money_format)
            worksheet.write(row, 3, item['fuel_cost'], money_format)
            worksheet.write(row, 4, item['total_cost'], money_format)
            worksheet.write(row, 5, item['last_service'].service_date.strftime('%Y-%m-%d') if item['last_service'] else 'N/A')
            worksheet.write(row, 6, f"{item['fuel_efficiency']:.2f} L/100km" if item['fuel_efficiency'] else 'N/A')

        workbook.close()
        return response

    def _generate_csv_report(self, data, start_date, end_date, total_maintenance, total_fuel):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=fleet_report_{start_date.strftime("%Y%m%d")}.csv'

        writer = csv.writer(response)
        writer.writerow(['Fleet Cost Report'])
        writer.writerow([f'Period: {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'])
        writer.writerow([f'Total Maintenance Cost: ${total_maintenance:,.2f}'])
        writer.writerow([f'Total Fuel Cost: ${total_fuel:,.2f}'])
        writer.writerow([f'Total Fleet Cost: ${(total_maintenance + total_fuel):,.2f}'])
        writer.writerow([])

        # Write headers
        writer.writerow(['Rego', 'Make/Model', 'Maintenance Cost', 'Fuel Cost', 'Total Cost', 'Last Service', 'Fuel Efficiency'])

        # Write data
        for item in data:
            writer.writerow([
                item['rego'],
                item['make_model'],
                f"${item['maintenance_cost']:,.2f}",
                f"${item['fuel_cost']:,.2f}",
                f"${item['total_cost']:,.2f}",
                item['last_service'].service_date.strftime('%Y-%m-%d') if item['last_service'] else 'N/A',
                f"{item['fuel_efficiency']:.2f} L/100km" if item['fuel_efficiency'] else 'N/A'
            ])

        return response

def healthcheck(request):
    """
    Health check endpoint for monitoring.
    Checks database and redis connectivity.
    """
    health_status = {
        'status': 'healthy',
        'database': True,
        'redis': True,
        'errors': []
    }
    
    # Check database connection
    try:
        connections['default'].ensure_connection()
    except Exception as e:
        health_status['database'] = False
        health_status['status'] = 'unhealthy'
        health_status['errors'].append(f'Database error: {str(e)}')
        logging.error(f'Health check failed - Database: {str(e)}')
    
    # Check Redis connection
    try:
        redis_client = Redis.from_url(settings.REDIS_URL)
        redis_client.ping()
    except Exception as e:
        health_status['redis'] = False
        health_status['status'] = 'unhealthy'
        health_status['errors'].append(f'Redis error: {str(e)}')
        logging.error(f'Health check failed - Redis: {str(e)}')
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)