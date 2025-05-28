from django.urls import path
from .models import *
from .views import *

urlpatterns = [
    path('signup/', SignupView.as_view(), name="signup"),
    path('verify-otp/', VerifyOtpView.as_view(), name="verify_otp"),
    path('resend-otp/', ResendOtpView.as_view(), name="resend_otp"),
    path('update-user/', UpdateUserDetailsView.as_view(), name="update_user"),
    path('login/', LoginView.as_view(),name="login"),
    path('get-user-profile/', GetUserProfileView.as_view(), name="get-user-profile"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('generate-access-token/', GenerateAccessTokenView.as_view(), name="generate-access-token"),
      
]