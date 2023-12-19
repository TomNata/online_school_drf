from django.urls import path
from payment.views import PaymentListAPIView


urlpatterns = [
    path('payment/', PaymentListAPIView.as_view()),
]
