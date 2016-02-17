"""
Django settings for lighthouse project.

Generated by 'django-admin startproject' using Django 1.9.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []


# default for use in development, separate from actual production key
if DEBUG:
    SECRET_KEY = 'h)9lw!5*s@zz3rfz*za(b%eda_$k%9tm1tguhd2gre4l0ykoke'
else:
    SECRET_KEY = os.getenv('LIGHTHOUSE_SECRET_KEY')


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'apps.home',
    'apps.login',
    'apps.links',
    'apps.users',
    'apps.govuk_template',

    'taggit'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lighthouse.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.core.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.govuk_template.variables.globals',
            ],
        },
    },
]

WSGI_APPLICATION = 'lighthouse.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('LIGHTHOUSE_DB', 'lighthouse'),
        'USER': os.getenv('LIGHTHOUSE_DB_USER', 'lighthouse'),
        'PASSWORD': os.getenv('LIGHTHOUSE_DB_PASSWORD', ''),
        'HOST': os.getenv('LIGHTHOUSE_DB_HOST', ''),
        'PORT': os.getenv('LIGHTHOUSE_DB_PORT', ''),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

domain = 'django.contrib.auth.password_validation'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': '{}.UserAttributeSimilarityValidator'.format(domain)},
    {'NAME': '{}.MinimumLengthValidator'.format(domain)},
    {'NAME': '{}.CommonPasswordValidator'.format(domain)},
    {'NAME': '{}.NumericPasswordValidator'.format(domain)},
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-GB'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

# Enable pretty and useful colourful tests

TEST_RUNNER = 'rainbowtests.test.runner.RainbowDiscoverRunner'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

AUTHENTICATION_BACKENDS = [
    'apps.login.super_basic_auth_backend.SuperBasicAuth'
]
