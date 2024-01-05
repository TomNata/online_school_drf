import stripe
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from course.models import Course
from payment.models import Payment
from payment.serializers import PaymentSerializer
from payment.services import create_stripe_payment


class PaymentList(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('course', 'lesson', 'method',)
    ordering_fields = ('date',)


class PaymentCreate(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()

    def create(self, request, course_pk=None):
        """ Создание платежной сессии для оплаты подписки на курс"""

        course = Course.objects.get(pk=course_pk)
        data = {
            'user': self.request.user,
            'course': course,
            'method': "card"
            }

        new_payment = Payment.objects.create(**data)
        session = create_stripe_payment(course.name)
        new_payment.session_id = session.id
        new_payment.save()
        return Response({'Ссылка для оплаты курса': session['url']})


class PaymentView(generics.RetrieveAPIView):

    def get(self, request, session_id):
        """ Проверка статуса платежной сессии """

        stripe.api_key = settings.STRIPE_TEST_API_KEY
        payment_session = stripe.checkout.Session.retrieve(session_id)

        if payment_session['payment_status'] == "paid":
            payment = Payment.objects.filter(session_id=session_id).first()
            payment.is_paid = True
            payment.save()

        return Response({'status': payment_session['payment_status']})



