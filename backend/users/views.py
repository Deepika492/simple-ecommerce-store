from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "success": True,
                "message": "User registered successfully.",
                "data": {
                    "token": token.key,
                    "user": UserSerializer(user).data
                }
            }, status=status.HTTP_201_CREATED)
        
        formatted_errors = {}
        for field, err_list in serializer.errors.items():
            if isinstance(err_list, list) and len(err_list) > 0:
                formatted_errors[field] = str(err_list[0])
            elif isinstance(err_list, dict):
                first_k = next(iter(err_list))
                v = err_list[first_k]
                formatted_errors[field] = str(v[0] if isinstance(v, list) else v)
            else:
                formatted_errors[field] = str(err_list)

        first_error_msg = next(iter(formatted_errors.values())) if formatted_errors else "Registration failed."
        return Response({
            "success": False,
            "message": first_error_msg,
            "errors": formatted_errors
        }, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "success": True,
                "message": "Login successful.",
                "data": {
                    "token": token.key,
                    "user": UserSerializer(user).data
                }
            }, status=status.HTTP_200_OK)
            
        return Response({
            "success": False,
            "message": "Invalid username/email or password.",
            "errors": "Invalid username/email or password."
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        return Response({
            "success": True,
            "message": "Logged out successfully."
        }, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "success": True,
            "message": "Profile retrieved.",
            "data": {
                "user": UserSerializer(request.user).data
            }
        }, status=status.HTTP_200_OK)
