from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView, \
    UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from course.models import Course, Lesson, Subscription
from course.paginators import CourseLessonPaginator
from course.permissions import NotModerator, IsOwner, IsModeratorOrOwner, IsUser
from course.serializers import CourseSerializer, LessonSerializer, LessonCreateSerializer, SubscriptionSerializer, \
    CourseSubscriptionSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CourseLessonPaginator

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [NotModerator]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsModeratorOrOwner]
        elif self.action == 'destroy':
            self.permission_classes = [IsOwner]

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        new_course = serializer.save()
        new_course.owner = self.request.user
        new_course.save()

    def retrieve(self, request, pk=None):
        user = self.request.user
        queryset = Course.objects.all()
        course = get_object_or_404(queryset, pk=pk)
        Subscription.objects.filter(user=user).filter(course=course)
        serializer = CourseSubscriptionSerializer(course)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderator').exists():
            courses = Course.objects.all()
        else:
            courses = Course.objects.filter(owner=user)
        return courses


class LessonCreateView(CreateAPIView):
    serializer_class = LessonCreateSerializer
    permission_classes = [NotModerator]

    def perform_create(self, serializer):
        new_lesson = serializer.save()
        new_lesson.owner = self.request.user
        new_lesson.save()


class LessonDetailView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsModeratorOrOwner]


class LessonListView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = CourseLessonPaginator

    def get_queryset(self):
        user = self.request.user
        if not user.groups.filter(name='moderator').exists():
            lessons = Lesson.objects.filter(owner=user)
        else:
            lessons = Lesson.objects.all()
        return lessons


class LessonUpdateView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsModeratorOrOwner]


class LessonDeleteView(DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner]


class SubscriptionCreateView(CreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, pk=None):
        course = Course.objects.get(pk=pk)
        sub = Subscription.objects.filter(course=course, user=self.request.user).first()
        if not sub:
            serializer = self.get_serializer(
                data={
                    'user': self.request.user.pk,
                    'course': course.pk,
                    'is_active': True
                }
            )
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({'Вы подписались на обновления курса.'}, status=status.HTTP_201_CREATED)

        elif not sub.is_active:
            sub.is_active = True
            sub.save()
            return Response({'Вы вновь подписались на обновления курса.'}, status=status.HTTP_200_OK)
        else:
            return Response({'Вы уже подписаны на обновления курса.'}, status=status.HTTP_200_OK)


class SubscriptionDeleteView(DestroyAPIView):
    queryset = Subscription.objects.all()
    permission_classes = [IsUser]

    def destroy(self, request, *args, **kwargs):
        course_pk = self.kwargs.get('course_pk')
        course = Course.objects.get(pk=course_pk)
        sub = Subscription.objects.filter(course=course, user=self.request.user).first()
        sub.is_active = False
        sub.save()

        return Response({'Вы отписались от обновлений курса.'},
                        status=status.HTTP_204_NO_CONTENT)

