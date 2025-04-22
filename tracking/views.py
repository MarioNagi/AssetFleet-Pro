import csv
from datetime import datetime,timedelta
import pandas as pd
import logging
import re
from django.db.models import Max
from django.http import HttpResponseForbidden
import logging
from django.urls import reverse
from django.contrib.auth.views import LoginView
from .mixins import UserRequiredMixin, ManagerRequiredMixin, AdminRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Tool, Car, Transfer, OdometerReading, Maintenance
from .forms import ToolForm, CarForm, TransferForm, OdometerReadingForm, MaintenanceForm, ImportForm, UserUpdateForm

logger = logging.getLogger(__name__)

# ----- Admin Dashboard View -----
class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'tracking/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tools'] = Tool.objects.all()
        context['cars'] = Car.objects.all()
        context['users'] = User.objects.all()
        return context


# ----- Manager Dashboard View -----
class ManagerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'tracking/manager_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_state = self.request.user.profile.state
        context['tools'] = Tool.objects.filter(state=user_state).select_related('assigned_user')
        context['cars'] = Car.objects.filter(state=user_state).select_related('assigned_user')
        return context


# ----- User Dashboard View -----
class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'tracking/user_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cars'] = Car.objects.filter(assigned_user=self.request.user).select_related('assigned_user')
        return context


class CustomLoginView(LoginView):
    """
    Redirect users based on their access level after login.
    - admin -> Admin Dashboard
    - manager -> Manager Dashboard
    - user -> User Dashboard
    """
    template_name = 'registration/login.html'  # or wherever your login template is

    def get_success_url(self):
        user = self.request.user
        # Debug logging
        logger.debug(f"User authenticated? {user.is_authenticated}")
        logger.debug(f"User: {user.username}, Access level: {getattr(user.profile, 'access_level', None)}")

        # If the user somehow isn't authenticated, fallback
        if not user.is_authenticated:
            logger.debug("User is not authenticated, redirecting to login.")
            return reverse_lazy('account_login')

        # Make sure user has a related profile and an access_level
        if hasattr(user, 'profile') and user.profile.access_level:
            access_level = user.profile.access_level.lower()
            logger.debug(f"access_level is {user.profile.access_level}")
        # 1) Superuser & staff => Admin
        if user.is_superuser and user.is_staff:
            user.profile.access_level = 'Admin'
            user.profile.save()
            logger.debug(f"Updated access_level to {user.profile.access_level}")
            return reverse_lazy('admin_dashboard')

        # 2) Staff only => Manager
        elif user.is_staff:
            user.profile.access_level = 'Manager'
            user.profile.save()
            logger.debug(f"Access level (lowercased) = {access_level}")
            return reverse_lazy('manager_dashboard')

        # 3) Otherwise => Normal user
        else:
            user.profile.access_level = 'User'
            user.profile.save()
            logger.debug(f"Updated access_level to {user.profile.access_level}")
            return reverse_lazy('user_dashboard')

# --------- Dashboard View ---------
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'tracking/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_role = self.request.user.profile.access_level
        user_state = self.request.user.profile.state

        if user_role == 'user':
            context['cars'] = Car.objects.filter(assigned_user=self.request.user)
        elif user_role == 'manager':
            context['cars'] = Car.objects.filter(state=user_state)
            context['tools'] = Tool.objects.filter(state=user_state)
        elif user_role == 'admin':
            context['cars'] = Car.objects.all()
            context['tools'] = Tool.objects.all()

        return context

# User-Specific View (Only for Users)
class UserCarView(UserRequiredMixin, ListView):
    model = Car
    template_name = 'tracking/user_car_list.html'

    def get_queryset(self):
        return Car.objects.filter(assigned_user=self.request.user)
class ManagerToolListView(LoginRequiredMixin, ListView):
    """
    Manager can only see tools/assets in their assigned state.
    """
    model = Tool
    template_name = 'tracking/manager_tool_list.html'
    context_object_name = 'tools'

    def get_queryset(self):
        user = self.request.user
        print("ManagerCarListView - get_queryset called")  # Temporary debug
        if user.is_staff:
            user_state = self.request.user.profile.state
            logger.debug(f"ManagerToolListView - Fetching tools for manager in state: {user_state}")
            return Tool.objects.filter(state=user_state)
        logger.warning("ManagerToolListView - User does not have manager access or profile is missing.")
        return Tool.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'profile'):
            context['state'] = self.request.user.profile.state
            logger.debug(f"ManagerToolListView - Manager's state: {context['state']}")
        else:
            logger.error("ManagerToolListView - User profile is missing.")
        return context

class ManagerCarListView(LoginRequiredMixin, ListView):
    """
    Manager can only see cars/assets in their assigned state.
    """
    model = Car
    template_name = 'tracking/manager_car_list.html'
    context_object_name = 'cars'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug("ManagerCarListView initialized")
        
    def get_queryset(self):
        user = self.request.user
        print("ManagerCarListView - get_queryset called")  # Temporary debug
        if user.is_staff:
            user_state = self.request.user.profile.state
            logger.debug(f"ManagerCarListView - Fetching cars for manager in state: {user_state}")
            return Car.objects.filter(state=user_state)
        logger.warning("ManagerCarListView - User does not have manager access or profile is missing.")
        return Car.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['state'] = self.request.user.profile.state
        return context
    



# Admin-Specific View (Only for Admins)
class AdminCarView(AdminRequiredMixin, ListView):
    model = Car
    template_name = 'tracking/admin_car_list.html'

    def get_queryset(self):
        return Car.objects.all()

# --------- Tool Views ---------
class ToolListView(LoginRequiredMixin, ListView):
    model = Tool
    template_name = 'tracking/tool_list.html'
    context_object_name = 'tools'
    def get_queryset(self):
        queryset = super().get_queryset().select_related('assigned_user', 'assigned_car')
        user = self.request.GET.get('user')
        tool_name = self.request.GET.get('tool_name')
        state_filter = self.request.GET.get('state', '')
        brand = self.request.GET.get('brand')
        car = self.request.GET.get('car')

        if user:
            queryset = queryset.filter(assigned_user__id=user)
        if tool_name:
            queryset = queryset.filter(tool_name=tool_name)
        if state_filter:  # Apply filter if a state is selected
            queryset = queryset.filter(state=state_filter)    
        if brand:
            queryset = queryset.filter(brand=brand)
        if car:
            queryset = queryset.filter(assigned_car__rego=car)    
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all()
        context['tool_names'] = Tool.objects.values_list('tool_name', flat=True).distinct()
        context['states'] = Tool.objects.values_list('state', flat=True).distinct()
        context['brands'] = Tool.objects.values_list('brand', flat=True).distinct()
        context['cars'] = Car.objects.all().distinct()
        return context

class ToolCreateView(LoginRequiredMixin, CreateView):
    model = Tool
    form_class = ToolForm
    template_name = 'tracking/tool_form.html'
    success_url = reverse_lazy('tool-list')

class ToolUpdateView(LoginRequiredMixin, UpdateView):
    model = Tool
    form_class = ToolForm
    template_name = 'tracking/tool_form.html'
    success_url = reverse_lazy('tool-list')

class ToolDeleteView(LoginRequiredMixin, DeleteView):
    model = Tool
    template_name = 'tracking/tool_confirm_delete.html'
    success_url = reverse_lazy('tool-list')


# --------- Car Views ---------
class CarListView(LoginRequiredMixin, ListView):
    model = Car
    template_name = 'tracking/car_list.html'
    context_object_name = 'cars'
    def get_queryset(self):
        return super().get_queryset().select_related('assigned_user')

class CarCreateView(LoginRequiredMixin, CreateView):
    model = Car
    form_class = CarForm
    template_name = 'tracking/car_form.html'
    success_url = reverse_lazy('car_list')

class CarUpdateView(LoginRequiredMixin, UpdateView):
    model = Car
    form_class = CarForm
    template_name = 'tracking/car_form.html'
    success_url = reverse_lazy('car_list')

class CarDeleteView(LoginRequiredMixin, DeleteView):
    model = Car
    template_name = 'tracking/car_confirm_delete.html'
    success_url = reverse_lazy('car_list')


# --------- Odometer Reading Views ---------
class OdometerReadingListView(LoginRequiredMixin, ListView):
    model = OdometerReading
    template_name = 'tracking/odometer_list.html'
    context_object_name = 'odometer_readings'
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            # Admin can see all odometer readings
            return OdometerReading.objects.all().select_related('car')
        elif user.is_staff:
            # Manager can see readings for cars in their state
            user_state = user.profile.state
            return OdometerReading.objects.filter(car__state=user_state).select_related('car')
        else:
            # Normal user can only see readings for their assigned cars
            return OdometerReading.objects.filter(car__assigned_user=user).select_related('car')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_superuser:
            context['cars'] = Car.objects.all()
        elif user.is_staff:
            context['cars'] = Car.objects.filter(state=user.profile.state)
        else:
            context['cars'] = Car.objects.filter(assigned_user=user)
        return context

class OdometerReadingCreateView(LoginRequiredMixin, CreateView):
    model = OdometerReading
    form_class = OdometerReadingForm
    template_name = 'tracking/odometer_form.html'
    success_url = reverse_lazy('odometer-list')

class OdometerReadingUpdateView(LoginRequiredMixin, UpdateView):
    model = OdometerReading
    form_class = OdometerReadingForm
    template_name = 'tracking/odometer_form.html'
    success_url = reverse_lazy('odometer-list')

class OdometerReadingDeleteView(LoginRequiredMixin, DeleteView):
    model = OdometerReading
    template_name = 'tracking/odometer_confirm_delete.html'
    success_url = reverse_lazy('odometer-list')


# --------- Maintenance Views ---------
class MaintenanceRecordListView(LoginRequiredMixin, ListView):
    model = Maintenance
    template_name = 'tracking/maintenance_list.html'
    context_object_name = 'maintenance_records'
    def get_queryset(self):
        queryset = super().get_queryset().select_related('car')
        car_id = self.request.GET.get('car')
        user_state = self.request.user.profile.state
        user_role = self.request.user.profile.access_level

        if user_role == 'manager':
            queryset = queryset.filter(car__state=user_state)
        elif car_id:
            queryset = queryset.filter(car_id=car_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_role = self.request.user.profile.access_level
        if user_role == 'manager':
            context['cars'] = Car.objects.filter(state=self.request.user.profile.state)
        else:
            context['cars'] = Car.objects.all()
        return context

class MaintenanceRecordCreateView(LoginRequiredMixin, CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'tracking/maintenance_form.html'
    success_url = reverse_lazy('maintenance-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['item_formset'] = MaintenanceItemFormSet(self.request.POST)
        else:
            context['item_formset'] = MaintenanceItemFormSet()
        return context

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
        else:
            return self.render_to_response(self.get_context_data(form=form))

class MaintenanceRecordUpdateView(LoginRequiredMixin, UpdateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'tracking/maintenance_form.html'
    success_url = reverse_lazy('maintenance-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['item_formset'] = MaintenanceItemFormSet(self.request.POST, instance=self.object)
        else:
            context['item_formset'] = MaintenanceItemFormSet(instance=self.object)
        return context

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
        else:
            return self.render_to_response(self.get_context_data(form=form))

class MaintenanceRecordDeleteView(LoginRequiredMixin, DeleteView):
    model = OdometerReading
    template_name = 'tracking/odometer_confirm_delete.html'
    success_url = reverse_lazy('odometer-list')

    def dispatch(self, request, *args, **kwargs):
        # Check if the user is an admin
        if hasattr(request.user, 'profile') and request.user.profile.access_level != 'admin':
            # Return a 403 Forbidden response if the user is not an admin
            return HttpResponseForbidden("You do not have permission to delete odometer readings.")
        return super().dispatch(request, *args, **kwargs)

# --------- Transfer Views ---------
class TransferListView(LoginRequiredMixin, ListView):
    model = Transfer
    template_name = 'tracking/transfer_list.html'
    context_object_name = 'transfers'

class TransferCreateView(LoginRequiredMixin, CreateView):
    model = Transfer
    form_class = TransferForm
    template_name = 'tracking/transfer_form.html'
    success_url = reverse_lazy('transfer-list')


# --------- User Views ---------
class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'tracking/user_list.html'
    context_object_name = 'users'

class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'tracking/user_form.html'
    success_url = reverse_lazy('user-list')

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'tracking/user_form.html'
    success_url = reverse_lazy('user-list')

class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'tracking/user_confirm_delete.html'
    success_url = reverse_lazy('user-list')

# --------- Import View ---------
class ImportView(LoginRequiredMixin, FormView):
    form_class = ImportForm
    template_name = 'tracking/import_form.html'
    success_url = reverse_lazy('dashboard')

    def parse_date(self, date_str):
        """
        Attempts multiple formats to parse a date string into a datetime.date.
        """
        if date_str in [None, '', 'nan', 'NaN', 'NULL', 'None']:  # Handle empty values
            return None

        if isinstance(date_str, float):  # Handle Excel date (days since 1899-12-30)
            try:
                excel_epoch = datetime(1899, 12, 30)
                return (excel_epoch + timedelta(days=int(date_str))).date()
            except ValueError:
                return None



        date_formats = [
            '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%b-%y', '%d-%B-%Y', '%d-%b-%Y'
        ]
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                return parsed_date.date()
            except ValueError:
                continue
        raise ValueError(f"'{date_str}' has an invalid date format.")

    def form_valid(self, form):
        file = form.cleaned_data['file']
        import_type = form.cleaned_data['type']  # 'Tool' or 'Car'

        # Read file into a Pandas DataFrame
        df = pd.read_excel(file, dtype=str) if file.name.endswith('.xlsx') else pd.read_csv(file, dtype=str)
        df = df.fillna('')  # Replace NaN with empty string

        if import_type == 'Tool':
            # Find last used internal_number in KE-XXX format
            last_tool = Tool.objects.filter(internal_number__startswith='KE-').order_by('-internal_number').first()
            last_number = int(re.search(r'KE-(\d+)', last_tool.internal_number).group(1)) if last_tool else 0

            for _, row in df.iterrows():
                internal_number = str(row.get('internal_number', '')).strip()

                # Auto-generate internal_number if missing
                if not internal_number:
                    last_number += 1
                    internal_number = f"KE-{last_number}"

                # Print debug output to verify the row being processed
                print(f"Processing: internal_number={internal_number}, serial_number={row.get('serial_number', '')}")

                # Save the tool
                tool, created = Tool.objects.update_or_create(
                    internal_number=internal_number,
                    defaults={
                        'serial_number': str(row.get('serial_number', '')).strip() if row.get('serial_number') else None,
                        'tool_name': str(row.get('tool_name', '')).strip().lower(),
                        'brand': str(row.get('brand', 'Generic Brand')).strip(),
                        'description': str(row.get('description', '')).strip(),
                        'size': str(row.get('size', '')).strip(),
                        'store': str(row.get('store', 'Online')).strip(),
                        'state': str(row.get('state', 'NSW')).strip(),
                        'quantity': int(float(row.get('quantity', 1))) if row.get('quantity') else 1,
                        'calibration_date': self.parse_date(row['calibration_date'])
                        if 'calibration_date' in row and row['calibration_date'] and str(row['calibration_date']).strip().lower() != 'nan'
                        else None,
                        'assigned_user': User.objects.filter(username=str(row.get('assigned_user', '')).strip()).first()
                        if 'assigned_user' in row and row['assigned_user'] and str(row['assigned_user']).strip().lower() != 'nan'
                        else None,
                        'assigned_car': Car.objects.filter(rego=str(row.get('assigned_car', '')).strip()).first()
                        if 'assigned_car' in row and row['assigned_car'] and str(row['assigned_car']).strip().lower() != 'nan'
                        else None,
                        'estimated_cost': row.get('estimated_cost', None),
                    }
                )

                print(f"✅ Saved: {tool} (Created: {created})")  # Debugging output

        elif import_type == 'Car':
            # Import Cars
            for _, row in df.iterrows():
                Car.objects.update_or_create(
                    rego=row['rego'],
                    defaults={
                        'rego_expiry_date': self.parse_date(row['rego_expiry_date'])
                        if 'rego_expiry_date' in row and row['rego_expiry_date'] else None,
                        'purchase_date': self.parse_date(row['purchase_date'])
                        if 'purchase_date' in row and row['purchase_date'] else None,
                        'purchase_price': float(row.get('purchase_price', 0.0)),
                        'state': row.get('state', 'NSW'),
                        'make': row.get('make', ''),
                        'model': row.get('model', ''),
                        'vin_number': row.get('vin_number', ''),
                        'maintenance_sticker_date': self.parse_date(row['maintenance_sticker_date'])
                        if 'maintenance_sticker_date' in row and row['maintenance_sticker_date'] else None,
                        'manufacturing_year': row.get('manufacturing_year', None),  # Handle manufacturing year
                        'color': row.get('color', ''),  # Handle color
                        'body': row.get('body', ''),  # Handle body type
                    }
                )

        return super().form_valid(form)