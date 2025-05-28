import random
from .models import User
from rest_framework import status
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import permission_classes
from asgiref.sync import sync_to_async
from django.conf import settings
from .constants import *
from django.db.models import Q
from django.core.cache import cache
from .task import *
from .constants import *
from .custom_permissions import *

"""
Signup
"""
class SignupView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.data.get("first_name"):
            return Response({"message":"Enter first_name", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        if not request.data.get("last_name"):
            return Response({"message":"Enter last_name", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        if not request.data.get("email"):
            return Response({"message":"Enter email", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        # if not request.data.get("username"):
        #     return Response({"message":"Enter username", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        if not request.data.get("phone_number"):
            return Response({"message":"Enter phone_number", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        if not request.data.get("password"):
            return Response({"message":"Enter password", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        if not request.data.get("confirm_password"):
            return Response({"message":"Enter confirm_password", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        # if not request.data.get("user_role"):
        #     return Response({"message":"Enter user_role", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        
        if not request.data.get("password") == request.data.get("confirm_password"):
            return Response({"message":"Enter confirm_password", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)

        if User.objects.filter(email = request.data.get("email")).exists():
            return Response({"message":"Entered email is already registered.", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        
       
        
        user = User.objects.create(first_name = request.data.get("first_name"),
                                   last_name = request.data.get("last_name"),
                                   email = request.data.get("email"),
                                   phone_number = request.data.get("phone_number"),
                                   password = make_password(request.data.get("password")),
                                   is_email_verified=False,
                                   is_phone_verified = False,
                                   is_active = False,
                                #    user_role = request.data.get("user_role")
        )

        user_name = user.first_name.capitalize() +" "+user.last_name.capitalize()
        
        otp = random.randint(000000, 999999)
        user.otp = otp
        user.save()
        user_id = user.id
        cache.set(user_id, otp, timeout=30)


        data = UserSerializer(user, context={"request":request}).data
        send_signup_verification_email.delay(user.email, otp, user_name)
        return Response({"message":"Please check your email to verify your account.", "data":{"data":data, "otp":otp}, "status":status.HTTP_201_CREATED}, status=status.HTTP_200_OK)
          

"""
Verify otp
"""
class VerifyOtpView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.data.get("email"):
            return Response({"message":"Enter email", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        if not request.data.get("otp"):
            return Response({"message":"Enter otp", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        try:
            user = User.objects.get(email = request.data.get("email"))
            user_id = user.id
            if user.is_email_verified == True:
                return Response({"message":"Your account is already verified", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        except:
            return Response ({"message":"Entered email is not registered yet!", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        
        
        valid_otp = cache.get(user_id)

        if valid_otp is None:
            return Response({"message": "OTP is expired, click on resend OTP.", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        
        if int(request.data.get("otp")) == int(valid_otp):
            user.is_email_verified = True
            user.is_active = True
            user.save()
            data = UserSerializer(user).data

            return Response({"message":"Your account is verified successfully.", "data":data,"status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"Entered otp is wrong or expired.", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)


"""
Resend opt
"""
class ResendOtpView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.data.get("email"):
            return Response({"message":"Enter email", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        try:
            user = User.objects.get(email = request.data.get("email"))
            user_id = user.id

            if user.is_email_verified == True:
                return Response({"message":"Your account is already verified.", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)

            if cache.get(user_id) is not None:
                return Response({"message":"You already have an active OTP.", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
            
            otp = random.randint(000000, 999999)
            user.otp = otp
            user.save()
            cache.set(user_id, otp, timeout=30)
            return Response({"message":"OTP generated successfully", "data":otp, "status":status.HTTP_200_OK}, status=status.HTTP_200_OK)

        except:
            return Response ({"message":"Entered email is not registered yet!", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)

        
"""
Login
"""
class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        
        if not request.data.get("identifier"):
            return Response({"message":"Enter email or phone number to signin.", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        if not request.data.get("password"):
            return Response({"message":"Enter password", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        
        if not User.objects.filter(Q(email = request.data.get("identifier")) | Q(phone_number = request.data.get("identifier"))).exists():
            return Response({"message":"Entered email is not registered yet. ", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)

        user = authenticate(request, username=request.data.get("identifier"), password=request.data.get("password"))
       

        if user is not None and user.is_email_verified is not False :
            login(request, user)
            user.is_active = True
            user.save()
            refresh = RefreshToken.for_user(user)
            token= {"refresh_token": str(refresh),
                     "access_token": str(refresh.access_token)}
            data = UserSerializer(user).data
            return Response({"message":"User logged in successfully","data":data, "token":token, "status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"Your account is not yet verified.", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)


"""
Logout
"""
class LogoutView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self, request):
        if not request.data.get("refresh_token"):
            return Response ({"message":"Enter refresh token", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        token = RefreshToken(request.data.get("refresh_token"))
        token.blacklist()
        return Response({"message":"Token blacklisted successfully", "status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


















"""
Generate access token
"""
class GenerateAccessTokenView(APIView):
    def post(self, request):
        if not request.data.get("refresh_token"):
            return Response ({"message":"Enter refresh token", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        refresh = RefreshToken(request.data.get("refresh_token"))
        access_token= str (refresh.access_token)
        return Response({"message":"Refresh token generated successfully", "data":{"access_token":access_token}, "status":status.HTTP_200_OK}, status=status.HTTP_200_OK)




class GetUserProfileView(APIView):
    permission_classes = [IsAuthenticated, IsUser]
    def get(self,request, *args, **kwargs):
        user = request.user
        data = UserSerializer(user).data
        return Response({"message":"User profile retrieved successfully", "data":data, "status":status.HTTP_200_OK}, status=status.HTTP_200_OK)



class UpdateUserDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsUser]
    def patch(self, request, *args, **kwargs):
        if not request.data.get("id"):
            return Response({"message":"Enter user id to update.", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        
        user = User.objects.get(id = request.data.get("id"))
        serializer = UserSerializer(user, data=request.data, partial= True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"User details updated successfully", "data":serializer.data, "status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
        serializer.errors()
        return Response({"message":"Enter user id to get details", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)


