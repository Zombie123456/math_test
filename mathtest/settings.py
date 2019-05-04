"""
Django settings for mathtest project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9)di50d6p(@@#olkmrdmd(a(y=m4dwxi&a)v$y_3ma_epbl09o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

DEFAULT_REQUEST_RATE_LIMIT = '5/minute'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

START_APPS = [
    'account',
    'loginsvc',
    'question'
]

INSTALLED_APPS += START_APPS

THIRD_PARTY_APPS = [
    'rest_framework',
    'oauth2_provider',
    'captcha',
    'django_filters',
    'django_extensions',
    'django_aliyun_oss2',
    'corsheaders'
]


CORS_ORIGIN_ALLOW_ALL = True


INSTALLED_APPS += THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'mathtest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mathtest.wsgi.application'


OAUTH2_PROVIDER = {
    'SCOPES': {'read': 'Read scope', 'write': 'Write scope'},
    'ACCESS_TOKEN_EXPIRE_SECONDS': 60 * 60 * 24,  # 1 day
    'REFRESH_TOKEN_EXPIRE_SECONDS': 60 * 60 * 24 * 10,  # 10 day
    'OAUTH_DELETE_EXPIRED': True,
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'NON_FIELD_ERRORS_KEY': 'error_code'
}


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mysql',
        'USER': 'root',
        'PASSWORD': 'pass1234',
        'HOST': 'for_mysql',
        'PORT': '3306'
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


CELERY_RESULT_BACKEND = 'rpc://'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ROUTES = {
    'deal_overdue': {
        'queue': 'others',
        'routing_key': 'others'
    }
}

CELERYBEAT_SCHEDULE = {
    'delete_expired_token_every_minute': {
        'task': 'delete_expired_token',
        'schedule': 60,
    }
}


RABBITMQ_DEFAULT_USER = os.environ.get('RABBITMQ_DEFAULT_USER', 'mathtest')
RABBITMQ_DEFAULT_PASS = os.environ.get('RABBITMQ_DEFAULT_PASS', 'mathtest')
RABBITMQ_DEFAULT_VHOST = os.environ.get('RABBITMQ_DEFAULT_VHOST', 'mathtest')
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
BROKER_URL = (f'amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}'
              f'@{RABBITMQ_HOST}:5672/{RABBITMQ_DEFAULT_VHOST}')
BROKER_HEARTBEAT = int(os.environ.get('RABBITMQ_HOST', 0))

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_CACHE_LOCATION = '{}://{}:6379'.format(REDIS_HOST, REDIS_HOST)

CACHES = {
    'default': {
        "BACKEND": 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_CACHE_LOCATION,
        'TIMEOUT': 259200,
        'OPTIONS': {
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        }
    },
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_ROOT = 'static'
STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'upload')
MEDIA_URL = '/upload/'

log_level = 'DEBUG'
LOGGING = {
           'version': 1,
           'disable_existing_loggers': False,
           'formatters': {
               'verbose': {
                   'format': '[%(asctime)s][%(name)s:%(lineno)s][%(levelname)s] %(message)s',
                   'datefmt': '%Y/%b/%d %H:%M:%S'
               },
               'colored': {'()': 'colorlog.ColoredFormatter',
                           'format': '[%(log_color)s%(asctime)s%(reset)s][%(name)s:%(lineno)s][%(log_color)s%(levelname)s%(reset)s] %(message)s',
                           'datefmt': '%Y/%b/%d %H:%M:%S',
                           'log_colors': {'DEBUG': 'cyan',
                                          'INFO': 'green',
                                          'WARNING': 'bold_yellow',
                                          'ERROR': 'red',
                                          'CRITICAL': 'red,bg_white'},
                           'secondary_log_colors': {},
                           'style': '%'},
           },
           'handlers': {
               'console': {
                   'level': log_level,
                   'class': 'logging.StreamHandler',
                   'formatter': 'colored'
               },
               'mail_admins': {
                   'level': 'ERROR',
                   'class': 'django.utils.log.AdminEmailHandler',
               },
           },
           'loggers': {
               'django': {
                   'handlers': ['console'],
                   'propagate': True,
               },
               'django.request': {
                   'handlers': ['mail_admins'],
                   'level': 'ERROR',
               },
           }
}

__app_logging = {'handlers': ['console', ],
                 'level': log_level,
                 'propagate': True}
for proj_app in START_APPS:
    LOGGING.get('loggers').update({proj_app: __app_logging})

DEFAULT_FILE_STORAGE = 'django_aliyun_oss2.backends.AliyunMediaStorage'
STATICFILES_STORAGE = 'django_aliyun_oss2.backends.AliyunStaticStorage'

ACCESS_KEY_ID = 'LTAIb5I3lIEeE8G9'
ACCESS_KEY_SECRET = '9aEqviBE0CwMU5MOvF2ScIeWGltKoR'
END_POINT = 'oss-cn-hongkong.aliyuncs.com'
BUCKET_NAME = 'chalice'
ALIYUN_OSS_CNAME = ''
BUCKET_ACL_TYPE = 'public-read'
