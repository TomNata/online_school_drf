from rest_framework import serializers

from payment.serializers import PaymentSerializer
from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ('id',)


class UserViewSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'email', 'phone', 'city', 'avatar',)


class UserPaymentSerializer(serializers.ModelSerializer):
    payment_list = PaymentSerializer(source='payment', many=True, read_only=True)

    class Meta:
        model = User
        exclude = ('id',)

