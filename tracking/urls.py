from django.urls import path
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import views as auth_views
from .views import (
    DashboardView, UserCarView,   AdminCarView, CustomLoginView, ManagerToolListView,
    ManagerDashboardView, UserDashboardView, ToolListView, ToolCreateView, 
    ToolUpdateView, ToolDeleteView, CarListView, CarCreateView, CarUpdateView, 
    CarDeleteView, OdometerReadingListView, OdometerReadingCreateView, 
    OdometerReadingUpdateView, OdometerReadingDeleteView, MaintenanceRecordListView, 
    MaintenanceRecordCreateView, MaintenanceRecordUpdateView, MaintenanceRecordDeleteView, 
    TransferListView, TransferCreateView, ImportView, UserListView, UserCreateView, 
    UserUpdateView, UserDeleteView,ManagerCarListView
)

urlpatterns = [
    # Redirect root to the dashboard if authenticated, otherwise go to login
    path('', DashboardView.as_view(), name='dashboard'),  # Directly use the view
    
    # Auth + Password Reset
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'
    ), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Custom Login / Logout
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Dashboards (note the names)
    path('dashboard/', DashboardView.as_view(), name='dashboard'),  
    path('admin-dashboard/', DashboardView.as_view(), name='admin_dashboard'),
    path('manager-dashboard/', ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('user-dashboard/', UserDashboardView.as_view(), name='user_dashboard'),

    # Tools
    path('tools/', ToolListView.as_view(), name='tool-list'),
    path('tools/add/', ToolCreateView.as_view(), name='tool-add'),
    path('tools/<str:pk>/edit/', ToolUpdateView.as_view(), name='tool-edit'),
    path('tools/<str:pk>/delete/', ToolDeleteView.as_view(), name='tool-delete'),

    # Cars
    path('cars/', CarListView.as_view(), name='car_list'),
    path('cars/add/', CarCreateView.as_view(), name='car-add'),
    path('cars/<int:pk>/edit/', CarUpdateView.as_view(), name='car-edit'),
    path('cars/<int:pk>/delete/', CarDeleteView.as_view(), name='car-delete'),

    # Import
    path('import/', ImportView.as_view(), name='import'),

    # Odometer
    path('odometer-readings/', OdometerReadingListView.as_view(), name='odometer-list'),
    path('odometer-readings/add/', OdometerReadingCreateView.as_view(), name='odometer-add'),
    path('odometer-readings/<int:pk>/edit/', OdometerReadingUpdateView.as_view(), name='odometer-edit'),
    path('odometer-readings/<int:pk>/delete/', OdometerReadingDeleteView.as_view(), name='odometer-delete'),

    # Maintenance
    path('maintenance-records/', MaintenanceRecordListView.as_view(), name='maintenance-list'),
    path('maintenance-records/add/', MaintenanceRecordCreateView.as_view(), name='maintenance-add'),
    path('maintenance-records/<int:pk>/edit/', MaintenanceRecordUpdateView.as_view(), name='maintenance-edit'),
    path('maintenance-records/<int:pk>/delete/', MaintenanceRecordDeleteView.as_view(), name='maintenance-delete'),

    # Transfer
    path('transfers/', TransferListView.as_view(), name='transfer-list'),
    path('transfers/add/', TransferCreateView.as_view(), name='transfer-add'),

    # Users
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/add/', UserCreateView.as_view(), name='user-add'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user-edit'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
   
    # User Password Change
    path('users/<int:pk>/password/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html'), name='user-password-change'),


    # Car views by role
    path('user-cars/', UserCarView.as_view(), name='user-cars'),
    path('admin-cars/', AdminCarView.as_view(), name='admin-cars'),
    path('manager-cars/', ManagerCarListView.as_view(), name='manager-cars'),
    path('manager-tools/', ManagerToolListView.as_view(), name='manager-tools'),
    

]
