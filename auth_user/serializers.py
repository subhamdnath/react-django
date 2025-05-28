from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ["password", "is_superuser", "groups", "user_permissions",  "is_staff", "date_joined", "last_login","created_on", "updated_on", "is_admin"]
