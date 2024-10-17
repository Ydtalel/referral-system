from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema

from .utils import set_referral_code, get_referral_code, delete_referral_code

from .serializers import (
    UserSerializer,
    LoginSerializer,
    ReferralCodeSerializer,
    ReferralCodeByEmailSerializer,
    RegisterWithReferralSerializer,
    ReferralSerializer
)
from .models import ReferralCode

User = get_user_model()


# все декораторы @swagger_auto_schema(request_body=...) указаны для
# удобства тестирования


class RegisterView(APIView):
    """
    Представление для регистрации нового пользователя.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        """
        Обрабатывает POST-запрос для регистрации пользователя.
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Представление для входа пользователя в систему.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request):
        """
        Обрабатывает POST-запрос для входа пользователя.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data,
                            status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateReferralCodeView(APIView):
    """
    Представление для создания нового реферального кода.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ReferralCodeSerializer)
    def post(self, request):
        """
        Обрабатывает POST-запрос для создания реферального кода
        """
        serializer = ReferralCodeSerializer(data=request.data,
                                            context={'request': request})
        if serializer.is_valid():
            referral_code = serializer.save(user=request.user)
            set_referral_code(referral_code)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteReferralCodeView(APIView):
    """
    Представление для удаления реферального кода.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, code):
        """
        Обрабатывает DELETE-запрос для удаления реферального кода
        """
        try:
            referral_code = ReferralCode.objects.get(code=code,
                                                     user=request.user)
            referral_code.delete()
            delete_referral_code(code)
            return Response(
                {"message": "Referral code deleted successfully"},
                status=status.HTTP_204_NO_CONTENT
            )
        except ReferralCode.DoesNotExist:
            return Response(
                {"error": "Referral code not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class ReferralCodeByEmailView(APIView):
    """
    Представление для получения реферального кода по email-адресу.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ReferralCodeByEmailSerializer)
    def post(self, request):
        """
         Обрабатывает POST-запрос для получения активного реферального кода по
         email.
        """
        serializer = ReferralCodeByEmailSerializer(data=request.data)
        if serializer.is_valid():
            active_code = serializer.get_active_referral_code(
                serializer.validated_data['email'])
            if active_code:
                cached_code = get_referral_code(active_code.code)
                if cached_code:
                    return Response({
                        "referral_code": cached_code.code,
                        "expiration_date": cached_code.expiration_date
                    }, status=status.HTTP_200_OK)
                else:
                    return Response(
                        {"error": "Referral code not found in cache."},
                        status=status.HTTP_404_NOT_FOUND
                    )
            return Response(
                {"error": "No active referral code found or code has"
                          " expired"},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterWithReferralView(APIView):
    """
    Представление для регистрации нового пользователя с использованием
    реферального кода.
    """

    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegisterWithReferralSerializer)
    def post(self, request):
        """
        Обрабатывает POST-запрос для регистрации пользователя с реферальным
        кодом.
        """
        serializer = RegisterWithReferralSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully "
                                        "with referral code"},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReferralsView(APIView):
    """
    Представление для получения списка рефералов текущего пользователя.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Обрабатывает GET-запрос для получения рефералов текущего пользователя.
        """
        referrals = User.objects.filter(referred_by=request.user)
        serializer = ReferralSerializer(referrals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
