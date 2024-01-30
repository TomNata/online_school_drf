from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установка переменной окружения для настроек проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создание экземпляра объекта Celery
app = Celery('config')

# Загрузка настроек из файла Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение и регистрация задач из файлов tasks.py в приложениях Django
app.autodiscover_tasks()

# подключение Celery к брокеру сообщений.
# В новых версиях Celery поведение при подключении к брокеру изменилось, и теперь при запуске не происходит
# повторных попыток подключения по умолчанию.
app.conf.broker_connection_retry_on_startup = False
