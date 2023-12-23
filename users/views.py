from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import User
from users.permissions import IsSelfUser
from users.serializers import UserSerializer, UserPaymentSerializer, UserViewSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(user.password)
        user.save()

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        elif self.action in ['retrieve', 'list']:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsSelfUser]

        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update'] \
                and self.request.user == self.get_object():
            serializer_class = UserPaymentSerializer
        else:
            serializer_class = UserViewSerializer
        if self.action == 'create':
            serializer_class = UserSerializer
        return serializer_class

