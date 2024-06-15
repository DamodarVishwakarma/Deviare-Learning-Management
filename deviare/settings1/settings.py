from .setings_base import *
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '%vj35+iv2v-v3-m-t)%hfe=7&^ftvlfwsjwe+hqjy%44gggp%y'

ALLOWED_HOSTS = ["*"]

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

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

STATIC_ROOT = BASE_DIR

ADMIN_MEDIA_PREFIX = "/static/admin/"

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )

}


# CELERY STUFF
BROKER_URL = 'redis://deviareredis:6379'
CELERY_RESULT_BACKEND = 'redis://deviareredis:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Nairobi'
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'deviare-lp-stage',
        'USER': 'deviareroot',
        'PASSWORD': '7b3368d1-5449-4629-a682-9d013db82c2a',
        'HOST': 'deviaredb.cx8czfe03eic.us-west-2.rds.amazonaws.com',
        'PORT': '3306',
    },
}
DEPLOYMENT_ENV = 'testing'
COMPANY_NAME = None
 
KEYCLOAK_URL='https://identity.deviare.co.za/auth/'
KEYCLOAK_CLIENTID='api-backend'
KEYCLOAK_REALM= 'Deviare'
KEYCLOAK_CLIENTSECRET= '662ec2e3-2dda-43f6-a74c-4f58fc50ebbe'

KEYCLOAK_ADMINUSER= 'realmadmin@deviare.co.za'
KEYCLOAK_ADMINPASSWORD= 'longisland'

URL="http://platform.deviare.co.za/"

EMAIL_HOST = "outlook.office365.com"
EMAIL_HOST_USER = "noreply@deviare.co.za"
EMAIL_HOST_PASSWORD = "Lam82139"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

deviare_config = {
    "AWS_S3_ACCESS_KEY":os.getenv('AWS_ACCESS_KEY_ID'),
    "AWS_S3_SECRET_KEY":os.getenv('AWS_SECRET_ACCESS_KEY'),
    "AWS_S3_BUCKET_NAME":"elearn-stat",
    "SENDER_ADDRESS":"eb0035@engineerbabu.in",
    "MAIL_SUBJECT": "Test1",
    "EXCEL_NAME":"test",
    'CLIENT_ID':"86f1964d-f9eb-4c16-818f-2cb561e2a268",
    'CLIENT_SECRET':"a.dhEc_[cer@pUW4y8CJwcxBX4k24C@0",
    'MS_AUTHORITY':"https://login.microsoftonline.com",
    'MS_GRAPH_POINT': "https://graph.microsoft.com/v1.0{0}",
    'MS_OAUTH_REDIRECT_URL': "https://api-staging.deviare.co.za/read_outlook_mail"
}