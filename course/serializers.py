from rest_framework import serializers

from course.models import Lesson, Course


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('course', 'name', 'description', 'preview', 'video_url',)


class LessonCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    lessons_list = LessonSerializer(source='lesson', many=True, read_only=True)
    lessons_quantity = serializers.IntegerField(source='lesson.all.count', read_only=True)

    class Meta:
        model = Course
        fields = ('name', 'description', 'preview', 'lessons_quantity', 'lessons_list',)
