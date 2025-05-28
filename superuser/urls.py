from django.urls import path
from .models import *
from .views import *

urlpatterns = [
    path('user-list/', UserListView.as_view(), name="user_list"),
    path('delete-user/', DeleteUserView.as_view(), name="delete_user"),
    path('get-user-by-id/', GetUserByIdView.as_view(), name="get_user_by_id"),
   
    
    

    
]
