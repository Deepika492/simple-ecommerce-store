from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import UserProfile
from .validators import validate_email_address, validate_username_string, validate_password_strength

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser', 'date_joined']

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, error_messages={'required': 'Username is required.', 'blank': 'Username is required.'})
    email = serializers.CharField(required=True, error_messages={'required': 'Email is required.', 'blank': 'Email is required.'})
    password = serializers.CharField(write_only=True, required=True, error_messages={'required': 'Password is required.', 'blank': 'Password is required.'})
    confirm_password = serializers.CharField(write_only=True, required=True, error_messages={'required': 'Please confirm your password.', 'blank': 'Please confirm your password.'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'confirm_password']

    def validate_username(self, value):
        try:
            val = validate_username_string(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message)
            
        if User.objects.filter(username__iexact=val).exists():
            raise serializers.ValidationError("This username is already taken.")
        return val

    def validate_email(self, value):
        try:
            val = validate_email_address(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message)
            
        if User.objects.filter(email__iexact=val).exists():
            raise serializers.ValidationError("This email is already registered.")
        return val

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        username = attrs.get('username')
        email = attrs.get('email')

        if not confirm_password or password != confirm_password:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        # Validate password strength & rules
        try:
            validate_password_strength(password, username=username, email=email)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": e.message})

        # Run Django password validators configured in AUTH_PASSWORD_VALIDATORS
        try:
            temp_user = User(username=username or '', email=email or '')
            password_validation.validate_password(password, user=temp_user)
        except DjangoValidationError as e:
            first_msg = e.messages[0] if isinstance(e.messages, list) and e.messages else str(e)
            raise serializers.ValidationError({"password": first_msg})

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, error_messages={'required': 'Username or email is required.', 'blank': 'Username or email is required.'})
    password = serializers.CharField(write_only=True, required=True, error_messages={'required': 'Password is required.', 'blank': 'Password is required.'})

    def validate(self, attrs):
        username = attrs.get('username', '').strip()
        password = attrs.get('password', '')

        if not username or not password:
            raise serializers.ValidationError("Please provide both username/email and password.")

        # Support login via either username or email
        user = None
        if '@' in username:
            try:
                user_obj = User.objects.get(email__iexact=username)
                user = authenticate(username=user_obj.username, password=password)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                user = None
        else:
            user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username/email or password.")

        if not user.is_active:
            raise serializers.ValidationError("This account has been disabled.")

        attrs['user'] = user
        return attrs
