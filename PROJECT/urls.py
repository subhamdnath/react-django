
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth-user/', include("auth_user.urls")),
    path('superuser/', include("superuser.urls"))
    
]
