
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base.settings")

app = Celery("base")

# Читаем конфиг из settings.py (все переменные с префиксом CELERY_)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находим tasks.py во всех приложениях INSTALLED_APPS
app.autodiscover_tasks()
