from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

class UserRequiredMixin(AccessMixin):
    """Allows only 'User' role"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.profile.role != 'user':
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class ManagerRequiredMixin(AccessMixin):
    """Allows only 'Manager' role"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.profile.role != 'manager':
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(AccessMixin):
    """Allows only 'Admin' role"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.profile.role != 'admin':
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
