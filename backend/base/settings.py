from celery.schedules import crontab
from datetime import timedelta
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = bool(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")


# Application definition

INSTALLED_APPS = [
    "unfold",  # before django.contrib.admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'currency',
    'api.apps.ApiConfig',
    'tastypie',
    "channels",
    'wholesale',
    "crm",
    'corsheaders',
    'axes',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'base.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'wholesale.context_processors.selected_node',
            ],
        },
    },
]


WSGI_APPLICATION = 'base.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': '5432',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'ru-UA'

USE_THOUSAND_SEPARATOR = True

TIME_ZONE = 'Europe/Kyiv'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# # Включаем хэширование файлов
# STORAGES = {
#     "staticfiles": {
#         "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
#     },
# }

CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_METHODS = (
    # "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)
CORS_ALLOWED_ORIGINS = [
    'http://фщ:5500',
    "http://127.0.0.1:5500",
]

# CORS_ORIGINS_WHITELIST = ["http://85.238.113.16",
#                           "http://127.0.0.1:8000",
#                           ]
CORS_ALLOW_HEADERS = ('content-disposition', 'accept-encoding',
                      'content-type', 'accept', 'origin', 'Authorization')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    "version": 1,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
            'propagate': False,
        },
    }
}


CELERY_BROKER_URL = 'redis://redis:6379/0'

# Celery Beat: Периодические задачи

CELERY_BEAT_SCHEDULE = {
    'close-shifts-at-20:00': {
        'task': 'wholesale.tasks.close_shifts_at_end_of_day',
        'schedule': crontab(hour=20, minute=0),  # Каждый день в 20:00
    },
}

# Временная зона для Celery Beat
CELERY_TIMEZONE = 'UTC'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': os.environ.get("REQUIREPASS"),
        }
    }
}

CACHE_ALL_EXCHANGERS = 'exchangers_cache'
CACHE_ALL_CURRENCYS = 'currencys_cache'
CACHE_ALL_CURRENCY = 'currency_cache'


# UNFOLD = {
#     "STYLES": [
#         "admin/custom.css",
#     ],
# }

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]
ASGI_APPLICATION = "base.asgi.application"

REDIS_PASSWORD = os.environ.get("REQUIREPASS", "")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@redis:6379"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [f"{REDIS_URL}/0"],
        },
    },
}

AXES_FAILURE_LIMIT = 10  # 10 ошибок до бана.

AXES_COOLOFF_TIME = timedelta(minutes=10)

AXES_LOCKOUT_PARAMETERS = ["username"]

AXES_RESET_ON_SUCCESS = True

AXES_ENABLE_ACCESS_FAILURE_LOG = True

AXES_PROXY_COUNT = 1

AXES_HANDLER = "axes.handlers.cache.AxesCacheHandler"

UNFOLD = {
    "SITE_TITLE": "Админ ExPrivat",
    "SITE_HEADER": "ExPrivat Админ",
    "DASHBOARD_CALLBACK": "wholesale.views.dashboard_callback",
    # "SIDEBAR": {
    #     "navigation": [
    #         {
    #             "title": "CRM",
    #             "separator": True,
    #             "items": [
    #                 {
    #                     "title": "Клиенты",
    #                     "icon": "people",
    #                     "link": "/admin/crm/clientprofile/",
    #                 },
    #                 {
    #                     "title": "История клиентов",
    #                     "icon": "history",
    #                     "link": "/admin/crm/clientevent/",
    #                 },
    #             ],
    #         },
    #     ]
    # }
    # "SIDEBAR": {
    #     "navigation": [
    #         {
    #             "title": "Отчеты",
    #             "items": [
    #                 {
    #                     "title": "Отчеты смен",
    #                     "icon": "assessment",
    #                     "link": "/admin/wholesale/wholesaleorder/reports/",
    #                 },
    #             ],
    #         },
    #     ],
    # },
}
