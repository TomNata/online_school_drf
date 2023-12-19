from rest_framework import serializers

from payment.serializers import PaymentSerializer
from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'phone', 'city', 'avatar',)


class UserPaymentSerializer(serializers.ModelSerializer):
    payment_list = PaymentSerializer(source='payment', many=True)

    class Meta:
        model = User
        fields = ('email', 'phone', 'city', 'avatar', 'payment_list',)
