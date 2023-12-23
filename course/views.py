from rest_framework import viewsets
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView, \
    UpdateAPIView, DestroyAPIView

from course.models import Course, Lesson
from course.permissions import NotModerator, IsOwner, IsModeratorOrOwner
from course.serializers import CourseSerializer, LessonSerializer, LessonCreateSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [NotModerator]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            self.permission_classes = [IsModeratorOrOwner]
        elif self.action == 'destroy':
            self.permission_classes = [IsOwner]

        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        new_course = serializer.save()
        new_course.owner = self.request.user
        new_course.save()

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
