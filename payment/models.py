from django.db import models

from course.models import Course, Lesson
from users.models import User

PAYMENT_CHOICES = [
    ("cash", "наличные"),
    ("card", "перевод на счет"),
]


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь', related_name='payment')
    date = models.DateField(verbose_name='дата оплаты')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='payment')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, null=True, blank=True, related_name='payment')
    summ = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='сумма оплаты')
    method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, verbose_name='способ оплаты')

    def __str__(self):
        return f'Оплата {self.lesson if self.lesson else self.course} от {self.user}'

    class Meta:
        verbose_name = 'оплата'
        verbose_name_plural = 'оплаты'