from rest_framework.permissions import BasePermission


class IsModeratorOrOwner(BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='moderator').exists():
            return True
        return request.user == view.get_object().owner


class NotModerator(BasePermission):
    def has_permission(self, request, view):
        return not request.user.groups.filter(name='moderator').exists()


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user == view.get_object().owner

