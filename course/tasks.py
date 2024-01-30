from datetime import datetime, timedelta, date
import pytz
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from course.models import Subscription, Course, Lesson
from users.models import User


@shared_task
def send_mail_course_update(course_pk):
    """
    Отправка email сообщений пользователям, подписанным на курс.
    """
    users = [sub.user for sub in Subscription.objects.filter(course=course_pk, is_active=True)]
    course = Course.objects.get(pk=course_pk)
    send_mail(
        subject=f'Обновление курса {course.name}',
        message=f'Курс {course.name} был обновлён новыми материалами',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email for user in users]
    )
    print("Отправлено")


@shared_task
def check_time_for_mail():
    """
    Периодическая задача, которая контролирует момент времени,
    когда нужно направить сообщение об обновлении уроков курса.
    """
    # задано время ожидания для отправления письма
    wait_interval = timedelta(hours=0, minutes=4)
    # получение часового пояса из настроек для корректного использования datetime.now
    tz_default = pytz.timezone(settings.TIME_ZONE)
    # переменная для оценки времени ожидания (истекло или нет)
    start_time = datetime.now(tz_default) - wait_interval
    # ограничение вхождения объекта в следующий цикл проверки
    task_interval = settings.CELERY_BEAT_SCHEDULE['check_time_for_mail']['schedule']
    stop_time = start_time - task_interval
    time_filter = {'last_update__lte': start_time,
                   'last_update__gt': stop_time}
    for course in Course.objects.all():
        if Subscription.objects.filter(course=course.id, is_active=True).exists():
            if Lesson.objects.filter(**time_filter, course=course.id).exists():
                send_mail_course_update.delay(course.pk)


@shared_task
def check_user_activity():
    """ Периодическая задача, которая проверяет пользователей по дате
    последнего входа и, если пользователь не заходил более месяца,
    блокирует его.
    """
    month = timedelta(days=31)
    # Определение контрольной даты
    key_date = date.today() - month

    for user in User.objects.filter(is_active=True, last_login__lt=key_date):
        user.is_active = False
        user.save(update_fields=["is_active"])
        print('Пользователь заблокирован')
