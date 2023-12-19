from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from users.models import User
from users.serializers import UserSerializer, UserPaymentSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(user.password)
        user.save()

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserPaymentSerializer(user)
        return Response(serializer.data)




