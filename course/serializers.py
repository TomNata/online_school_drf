from rest_framework import serializers

from course.models import Lesson, Course, Subscription
from course.validators import UrlValidator


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class LessonCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        exclude = ('id',)
        validators = [UrlValidator(field='video_url')]


class CourseSerializer(serializers.ModelSerializer):
    lessons_list = LessonSerializer(source='lesson', many=True, read_only=True)
    lessons_quantity = serializers.IntegerField(source='lesson.all.count', read_only=True)

    class Meta:
        model = Course
        fields = ('name', 'description', 'preview', 'lessons_quantity', 'lessons_list',)


class CourseSubscriptionSerializer(serializers.ModelSerializer):
    lessons_list = LessonSerializer(source='lesson', many=True, read_only=True)
    lessons_quantity = serializers.IntegerField(source='lesson.all.count', read_only=True)
    subscription = serializers.BooleanField(source='subscription.exists')

    class Meta:
        model = Course
        fields = ('name', 'description', 'preview', 'lessons_quantity', 'subscription', 'lessons_list',)


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'

