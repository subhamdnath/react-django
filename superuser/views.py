from rest_framework import status
from auth_user.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from auth_user.serializers import UserSerializer
from auth_user.custom_permissions import *
from rest_framework.permissions import IsAuthenticated
from auth_user.pagination import *


class UserListView(APIView):
    def get(self, request, *args, **kwargs):
        users = User.objects.all().order_by("-id")
        data = UserSerializer(users, many=True).data
        return Response({"message":"User list retrieved.", "data":data, "status":status.HTTP_200_OK}, status=status.HTTP_200_OK)
    

class DeleteUserView(APIView):
    def delete(self, request, *args, **kwargs):
        if not request.query_params.get("id"):
            return Response({"message":"Enter user id to delete", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        user = User.objects.get(id = request.query_params.get("id"))
        user.delete()
        return Response({"message":"User deleted successfully.", "status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


class GetUserByIdView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.query_params.get("id"):
            return Response({"message":"Enter user id to get details", "status":status.HTTP_400_BAD_REQUEST}, status=status.HTTP_200_OK)
        user = User.objects.get(id = request.query_params.get("id"))
        data = UserSerializer(user).data
        return Response({"message":"User details retrieved successfully.", "data":data, "status":status.HTTP_200_OK}, status=status.HTTP_200_OK)


