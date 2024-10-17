from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import (RegisterView, LoginView, CreateReferralCodeView,
                    DeleteReferralCodeView, ReferralCodeByEmailView,
                    RegisterWithReferralView, ReferralsView)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="Referral API",
        default_version='v1',
        description="API documentation for the referral system",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('referral-code/create/', CreateReferralCodeView.as_view(),
         name='create_referral_code'),
    path('referral-code/delete/<uuid:code>/', DeleteReferralCodeView.as_view(),
         name='delete_referral_code'),

    path('referral-code/by-email/', ReferralCodeByEmailView.as_view(),
         name='referral_code_by_email'),
    path('register-with-referral/', RegisterWithReferralView.as_view(),
         name='register_with_referral'),
    path('referrals/', ReferralsView.as_view(), name='referrals'),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]
