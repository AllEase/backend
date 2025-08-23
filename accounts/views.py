import jwt
import datetime
from django.http import JsonResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from mongoengine.errors import NotUniqueError
from .models import UserLogin




def generate_jwt(user_id):
    payload = {
        "user_id": str(user_id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.JWT_EXPIRATION_SECONDS),
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


class SignupView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if UserLogin.objects(username=username).first():
            return JsonResponse({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        user = UserLogin(username=username, email=email)
        user.set_password(password)
        user.save()

        token = generate_jwt(user.id)
        return JsonResponse({"message": "Signup successful", "token": token}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = UserLogin.objects(username=username).first()
        if not user or not user.check_password(password):
            return JsonResponse({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        token = generate_jwt(user.id)
        return JsonResponse({"message": "Login successful", "token": token}, status=status.HTTP_200_OK)
