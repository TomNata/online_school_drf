from django.urls import path

from payment.apps import PaymentConfig
from payment.views import PaymentList, PaymentCreate, PaymentView

app_name = PaymentConfig.name

urlpatterns = [
    path('payment/', PaymentList.as_view(), name='payment'),
    path('payment/create/<int:course_pk>/', PaymentCreate.as_view(), name='payment-add'),
    path('payment/<str:session_id>/', PaymentView.as_view(), name='payment-view'),
]
