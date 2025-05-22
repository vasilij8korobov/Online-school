from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import PaymentViewSet, UserViewSet, RegisterView, CustomTokenObtainPairView, \
    StripePaymentCreateAPIView, PaymentSuccessAPIView, PaymentCancelAPIView

router = DefaultRouter()
router.register(r'payments', PaymentViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('payments/stripe/<int:course_id>/', StripePaymentCreateAPIView.as_view(), name='create-stripe-payment'),
    path('payments/success/', PaymentSuccessAPIView.as_view(), name='payment-success'),
    path('payments/cancel/', PaymentCancelAPIView.as_view(), name='payment-cancel'),

]
