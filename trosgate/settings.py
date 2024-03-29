"""
Django settings for trosgate project.

Generated by 'django-admin startproject' using Django 4.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path
from django.contrib.messages import constants as messages
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, ".env"))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = False
# DEBUG = True

# ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
ALLOWED_HOSTS = ['trosgate.com', '159.65.115.95']

AUTH_USER_MODEL = 'account.Customer'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Custom Apps
    'account',
    'vendors',
    'general_settings',
    'custodians',
    'future',
    'onboarding',
    'tickets',
    'widget_tweaks',
    'ckeditor',
    'reports',
    'inventory',
    "django_htmx",
    'django_celery_results',
    'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'account.middleware.GatewayMiddleware',
]

ROOT_URLCONF = 'trosgate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'general_settings.context_processors.website',
                'vendors.context_processors.active_team',
            ],
            'libraries':  {
                'trackertag': 'reports.templatetags.trackertag',
            }
        },
    },
]

WSGI_APPLICATION = 'trosgate.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

#SERVER SIDE
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'trosgate',
        'USER': 'katey',
        'PASSWORD': 'Prof2ike.y2ky2k',
        'HOST': 'localhost',
        'PORT': '',
    }
}

#LOCAL DATABASE
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'banking',
#         'USER': 'katey',
#         'PASSWORD': 'Prof2ike.y2ky2k',
#         'HOST': 'localhost',
#         'PORT': '',
#     }
# }


# Twilio SendGrid
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'apikey'
# EMAIL_HOST_PASSWORD = "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"


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Accra'
USE_I18N = True
USE_TZ = True

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles/')
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# MEDIA PATH FOR TROSGATE SOFTWARE
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# LOGIN AND AUTHENTICATION FOR TROSGATE SOFTWARE
LOGIN_URL = "account:homepage"
LOGIN_REDIRECT_URL = "account:dashboard"
LOGOUT_REDIRECT_URL = "account:homepage"

#Custom Email Backend for Trosgate software
EMAIL_BACKEND = 'general_settings.backends.MailerBackend'

####option one for email setup in development mode###
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ADMINS = (
    ('Ivendor', 'myvoistudio@gmail.com'),
)
MANAGERS = ADMINS

# CKeditor Config
CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
CKEDITOR_CONFIGS = {
    'default': {
        'width': '100%',
        'tabSpaces': 4,
    }
}

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
}

PASSWORD_RESET_TIMEOUT = 1209600 #two weeks in seconds
USE_THOUSAND_SEPARATOR = True
EMAIL_USE_LOCALTIME = True

# USE_TZ = True
TIMEZONE = 'Africa/Accra'


if not DEBUG:
    SESSION_EXPIRE_AT_BROWSER_CLOSE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_AGE = 1209600 #two weeks in seconds
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    CSRF_COOKIE_SECURE = True
    EMAIL_SUBJECT_PREFIX = '[Ivendor]'


# EMAIL PASS LATEST: yqwvhebpxtgqmjph

# CELERY CONFIGURATIONS
CELERY_BROKER_URL = 'redis://127.0.0.1:6379'  #Either this in settings file, or use as 'broker_url' variable in celery.py
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Accra' 

# STORAGE CHOICE OF CELERY TASKS
CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_EXTENDED = True

# CELERY BEAT CONFIGURATIONS
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

MAXIMUM_INVITE_SIZE = 10
# PASSWORD_RESET_TIMEOUT_DAYS =
