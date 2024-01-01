from django.db import models
from users.models import NULLABLE, User


class Course(models.Model):
    name = models.CharField(max_length=150, verbose_name='Название курса')
    preview = models.ImageField(upload_to='course/', verbose_name='Картинка', **NULLABLE)
    description = models.TextField(verbose_name='Описание курса ')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='автор', **NULLABLE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ('id',)


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lesson')
    name = models.CharField(max_length=150, verbose_name='Название урока')
    description = models.TextField(verbose_name='Описание урока')
    preview = models.ImageField(upload_to='course/lesson', verbose_name='Картинка', **NULLABLE)
    video_url = models.URLField(verbose_name='ссылка на видео', **NULLABLE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='автор', **NULLABLE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ('course', 'id',)


class Subscription(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subscription', **NULLABLE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь', **NULLABLE)
    is_active = models.BooleanField(**NULLABLE)

    def __str__(self):
        return f'{self.user} {"подписан" if self.is_active else "не подписан"} на курс "{self.course}"'

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'


