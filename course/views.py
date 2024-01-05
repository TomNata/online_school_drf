from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
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

    @swagger_auto_schema(operation_id="Создание урока")
    def post(self, request, *args, **kwargs):
        return super(LessonCreateView, self).post(request, *args, **kwargs)


class LessonDetailView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsModeratorOrOwner]

    @swagger_auto_schema(operation_id="Информация об уроке")
    def get(self, request, *args, **kwargs):
        return super(LessonDetailView, self).get(request, *args, **kwargs)


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

    @swagger_auto_schema(operation_id="Список уроков")
    def get(self, request, *args, **kwargs):
        return super(LessonListView, self).get(request, *args, **kwargs)


class LessonUpdateView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsModeratorOrOwner]

    @swagger_auto_schema(operation_id="Редактирование урока")
    def put(self, request, *args, **kwargs):
        return super(LessonUpdateView, self).put(request, *args, **kwargs)

    @swagger_auto_schema(operation_id="Частичное редактирование урока")
    def patch(self, request, *args, **kwargs):
        return super(LessonUpdateView, self).patch(request, *args, **kwargs)


class LessonDeleteView(DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner]

    @swagger_auto_schema(operation_id="Удаление урока")
    def delete(self, request, *args, **kwargs):
        return super(LessonDeleteView, self).delete(request, *args, **kwargs)


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

    @swagger_auto_schema(operation_id="Отключение подписки")
    def delete(self, request, *args, **kwargs):
        return super(SubscriptionDeleteView, self).delete(request, *args, **kwargs)

