from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from referrals.hunter_services import verify_email
from referrals.models import ReferralCode

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и валидации пользователя.
    """

    def validate_email(self, value):
        """
        Проверяет валидность указанного email-адреса.
        """
        result = verify_email(value)
        if result and result['data']['status'] != 'valid':
            raise serializers.ValidationError(
                "The email address is invalid or cannot be used.")

        return value

    def create(self, validated_data):
        """
        Создаёт нового пользователя.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор для аутентификации пользователя.
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Проверяет предоставленные учетные данные и возвращает токены.
        """
        user = User.objects.filter(username=data['username']).first()
        if user and user.check_password(data['password']):
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        raise serializers.ValidationError("Invalid credentials")


class ReferralCodeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с реферальными кодами.
    """

    def validate_expiration_date(self, value):
        """
        Проверяет, что срок реферального кода не истек.
        """
        if value <= timezone.now():
            raise serializers.ValidationError("Expiration date cannot be in "
                                              "the past.")
        return value

    class Meta:
        model = ReferralCode
        fields = ['code', 'expiration_date', 'is_active', 'user']
        read_only_fields = ['code', 'is_active', 'user']


class ReferralCodeByEmailSerializer(serializers.Serializer):
    """
    Сериализатор для получения реферального кода по email.
    """

    email = serializers.EmailField()

    def validate_email(self, value):
        """
        Проверяет, существует ли пользователь с указанным email.
        """
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "User with this email does not exist.")
        return value

    def get_active_referral_code(self, email):
        """
        Получает активный реферальный код для указанного email.
        """
        user = User.objects.get(email=email)
        active_code = ReferralCode.objects.filter(user=user,
                                                  is_active=True).first()

        if active_code and not active_code.is_expired():
            return active_code
        return


class RegisterWithReferralSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя с возможностью указания
    реферального кода.
    """

    referral_code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'referral_code']

    def validate_email(self, value):
        """
        Проверяет валидность указанного email-адреса через сторонний сервис.
        """
        verification_result = verify_email(value)
        if verification_result:
            if not verification_result['data']['status'] == 'valid':
                raise serializers.ValidationError("Invalid email address.")
        else:
            raise serializers.ValidationError("Error checking email validity.")
        return value

    def create(self, validated_data):
        """
        Создаёт нового пользователя и применяет реферальный код, если он указан
        """
        referral_code = validated_data.pop('referral_code', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        if referral_code:
            try:
                referral = ReferralCode.objects.get(code=referral_code,
                                                    is_active=True)
                if referral.is_expired():
                    raise serializers.ValidationError(
                        "Referral code has expired.")
                user.referred_by = referral.user
                user.save()
            except ReferralCode.DoesNotExist:
                raise serializers.ValidationError("Invalid referral code.")
        return user


class ReferralSerializer(serializers.ModelSerializer):
    """
    Сериализатор для получения информации о пользователе с реферальным кодом.
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email']
