from django.core.management import BaseCommand

from course.models import Course, Lesson
from payment.models import Payment
from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        payment_list = [
            {'user': User.objects.get(pk=1), 'date': '2023-11-11', 'course': Course.objects.get(pk=2),
             'lesson': None, 'summ': 157600.00, 'method': 'card'},
            {'user': User.objects.get(pk=2), 'date': '2023-11-25', 'course': None,
             'lesson': Lesson.objects.get(pk=7), 'summ': 3500.00, 'method': 'card'},
            {'user': User.objects.get(pk=2), 'date': '2023-11-30', 'course': None,
             'lesson': Lesson.objects.get(pk=8), 'summ': 4000.00, 'method': 'card'},
            {'user': User.objects.get(pk=1), 'date': '2023-12-15', 'course': None,
             'lesson': Lesson.objects.get(pk=8), 'summ': 4000.00, 'method': 'card'},
        ]

        for payment in payment_list:
            Payment.objects.create(**payment)
