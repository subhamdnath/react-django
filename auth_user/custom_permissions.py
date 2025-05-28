from rest_framework.permissions import BasePermission
from .models import *
from .constants import *


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_role == "ADMIN"

class IsUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_role == "USER"

    
