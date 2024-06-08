# user/views.py
"""
This file contains views for user operations.
"""

from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import CustomUser
from .serializers import (
    UserSerializer, SignupSerializer, LoginSerializer,
    PasswordResetSerializer, UpdateUsernameSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['GET'])
@permission_classes([AllowAny])
def index(request):
    return Response({"message": "Welcome to RRA Report Management System"}, status=status.HTTP_200_OK)

class SignupView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class UserDetailView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class UserUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class UserDeleteView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class UserByUsernameView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs['username']
        return CustomUser.objects.filter(username=username)

class UserByEmailView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        email = self.kwargs['email']
        return CustomUser.objects.filter(email=email)

class UserByPhoneView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        phone = self.kwargs['phone']
        return CustomUser.objects.filter(phone=phone)

class UserByFirstNameView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        first_name = self.kwargs['first_name']
        return CustomUser.objects.filter(first_name__icontains=first_name)

class UserByLastNameView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        last_name = self.kwargs['last_name']
        return CustomUser.objects.filter(last_name__icontains=last_name)

class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')
            
            
            user = None
            if username:
                user = CustomUser.objects.filter(username=username).first()
            elif email:
                user = CustomUser.objects.filter(email=email).first()
            elif phone:
                user = CustomUser.objects.filter(phone=phone).first()

            if user:
                # new_password = self.generate_random_string(6)
                new_password = request.data.get('new_password')
                user.set_password(new_password)
                user.save()

                # Send new password via email
                self.send_credentials(user.email, user.username, new_password)

                return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)

            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def generate_random_string(self, length):
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def send_credentials(self, email, username, new_password):
        from django.core.mail import send_mail
        send_mail(
            'Password Reset for RRA Report Management System',
            f'Hello,\n\nYour password has been reset. Here are your new credentials:\n\nUsername: {username}\nPassword: {new_password}\n\nYou can change these credentials after logging in.\n\nRegards!',
            'from@example.com',
            [email],
            fail_silently=False,
        )

class UpdateUsernameView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UpdateUsernameSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            phone = serializer.validated_data.get('phone')
            new_username = serializer.validated_data.get('new_username')
            
            user = None
            if email:
                user = CustomUser.objects.filter(email=email).first()
            elif phone:
                user = CustomUser.objects.filter(phone=phone).first()

            if user:
                user.username = new_username
                user.save()
                return Response({"message": "Username updated successfully"}, status=status.HTTP_200_OK)

            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = CustomUser.objects.count()
        return Response({"count": count}, status=status.HTTP_200_OK)

class UserTrendView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta

        def get_trend(interval):
            end_date = timezone.now()
            start_date = end_date - interval
            return CustomUser.objects.filter(created_at__range=(start_date, end_date)).count()

        trends = {
            "daily": get_trend(timedelta(days=1)),
            "weekly": get_trend(timedelta(weeks=1)),
            "monthly": get_trend(timedelta(days=30)),
            "yearly": get_trend(timedelta(days=365)),
            "five_years": get_trend(timedelta(days=365*5)),
            "ten_years": get_trend(timedelta(days=365*10)),
        }

        return Response(trends, status=status.HTTP_200_OK)
