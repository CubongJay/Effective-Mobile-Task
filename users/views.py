from django.shortcuts import get_object_or_404

from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Users
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import CustomTokenObtainPairSerializer, UserSerializer
from .constants import UserRole

# Create your views here.


class UsersListCreateView(ListCreateAPIView):
    queryset = Users.objects.all()

    serializer_class = UserSerializer

    def get_permissions(self):

        if self.request.method == "POST":
            return [AllowAny()]
        else:
            return [IsAuthenticated()]


class UserDeleteView(APIView):

    def delete(self, request, pk=None):
        if pk is None:
            user = request.user
        else:
            user = get_object_or_404(Users, pk=pk)

        if not user.is_active:
            return Response(
                {"error": "User is already deactivated"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = False

        user.save()

        return Response(
            {"message": f"User {user.email} successfuly deactivated"},
            status=status.HTTP_200_OK,
        )


class UserUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk=None):
        if pk is None:
            user = request.user
        else:
            is_admin = getattr(request.user, "role", "user") == UserRole.ADMIN.value
            is_self = request.user.id == pk
            if not (is_self or is_admin):
                return Response(
                    {"error": "You do not have permission to update this user"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            user = get_object_or_404(Users, pk=pk)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT view that uses email instead of username"""

    serializer_class = CustomTokenObtainPairSerializer
