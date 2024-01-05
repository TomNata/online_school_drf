from django.core.management import BaseCommand
from course.models import Course, Lesson
from payment.models import Payment
from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        #Payment.objects.all().delete()
        payment_list = [
            {'user': User.objects.get(email='kim@yandex.ru'), 'date': '2023-11-11',
             'course': Course.objects.get(name='Python developer'), 'lesson': None,
             'summ': 157600.00, 'method': 'card'
             },
            {'user': User.objects.get(email='popov@yandex.ru'), 'date': '2023-11-25', 'course': None,
             'lesson': Lesson.objects.get(name='NumPy'), 'summ': 3500.00, 'method': 'card'
             },
            {'user': User.objects.get(email='ivanova@mail.ru'), 'date': '2023-11-30', 'course': None,
             'lesson': Lesson.objects.get(name='Pandas'), 'summ': 4000.00, 'method': 'card'
             },
            {'user': User.objects.get(email='titov@yandex.ru'), 'date': '2023-12-15', 'course': None,
             'lesson': Lesson.objects.get(name='DjangoORM'), 'summ': 4000.00, 'method': 'card'
             },
        ]

        for payment in payment_list:
            Payment.objects.create(**payment)
