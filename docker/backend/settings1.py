#from .settings_base import *
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'faz=5)l!bf(vai6n^d0w4acb*tw#6!$vu730=66-9-s-u#bv%s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# AUTH_USER_MODEL = 'main.User'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'main.apps.MainConfig',
    'project.apps.ProjectConfig',
    'services.apps.ServicesConfig',
    'django_crontab',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'deviare.urls'

CORS_ORIGIN_ALLOW_ALL = True

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

WSGI_APPLICATION = 'deviare.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'deviare-lp-stage',
            'USER': 'deviareroot',
            'PASSWORD': '7b3368d1-5449-4629-a682-9d013db82c2a',
            'HOST': 'deviaredb.cx8czfe03eic.us-west-2.rds.amazonaws.com',
            'PORT': '3306',
        },
    # 'db2' : {
    #         'ENGINE': 'django.db.backends.mysql',
    #         'NAME': 'deviare-lp-stage',
    #         'USER': 'deviareroot',
    #         'PASSWORD': '7b3368d1-5449-4629-a682-9d013db82c2a',
    #         'HOST': 'deviaredb.cx8czfe03eic.us-west-2.rds.amazonaws.com',
    #         'PORT': '3306',
    # }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'outlook.office365.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'noreply@deviare.co.za'
EMAIL_HOST_PASSWORD = 'Lam82139'


KEYCLOAK_URL="https://identity.deviare.co.za/auth/"
KEYCLOAK_REALM= "Deviare"
KEYCLOAK_CLIENTID="api-backend"
KEYCLOAK_CLIENTSECRET= "662ec2e3-2dda-43f6-a74c-4f58fc50ebbe"
KEYCLOAK_ADMINUSER= "realmadmin@deviare.co.za"
KEYCLOAK_ADMINPASSWORD= "longisland"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )

}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

URL="https://api-staging.deviare.co.za/"

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/


STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
STATIC_ROOT = BASE_DIR
ADMIN_MEDIA_PREFIX = "/static/admin/"


deviare_config = {
    "AWS_S3_ACCESS_KEY":"AKIA2GPDX7TKLYXM345H",
    "AWS_S3_SECRET_KEY":"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",
    "AWS_S3_BUCKET_NAME":"elearn-stat",
    # "SENDER_ADDRESS":"eb0035@engineerbabu.in",
    # "MAIL_SUBJECT": "Test123",
    # "EXCEL_NAME":"tst12",
    # 'CLIENT_ID':'86f1964d-f9eb-4c16-818f-2cb561e2a268',
    # 'CLIENT_SECRET':'a.dhEc_[cer@pUW4y8CJwcxBX4k24C@0',
    # 'MS_AUTHORITY':'https://login.microsoftonline.com',
    # 'MS_GRAPH_POINT': 'https://graph.microsoft.com/v1.0{0}',
    # 'MS_OAUTH_REDIRECT_URL': 'https://127.0.0.1:8000/read_outlook_mail'
}

CRONJOBS = [
    ('* 8 * * *', 'main.utils.sl_cron_job')
]