from rest_framework.permissions import BasePermission

from course.models import Subscription, Course


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


class IsUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        obj = Course.objects.get(pk=request.course_pk)
        subscription_obj = Subscription.objects.filter(course=obj).\
            filter(user=request.user).\
            filter(is_active=True)
        return subscription_obj.exists()
