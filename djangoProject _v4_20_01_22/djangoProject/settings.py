"""
Django settings for djangoProject project.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir=r"C:\Program Files\instantclient_21_3")
# Build paths inside the project like this: BASE_DIR / 'subdir'.
#ścieżka projektu
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# Sekretny klucz produkcji, najlepiej go jeszcze trochę zmienić
SECRET_KEY = 'django-insecure-#xjsk@qmb0%a530=9bxl=@@qw-aaun8a%wmmt-bu(@g6f+e2u1'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition
#Tutaj dodajemy nowo stworzone modele (aplikacje)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'page',

]

#Komponenty związane z bezpieczeństwem (?) m.in.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

#Dzięki temu nasz projekt radzi sobie z adresami URL np /admin
ROOT_URLCONF = 'djangoProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR / 'templates'/ 'account']
        ,
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

WSGI_APPLICATION = 'djangoProject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


DATABASES={
    'default':
    {
    'ENGINE':'django.db.backends.oracle',
    'NAME':'db202112131719_high',
    'USER':'ADMIN',
    'PASSWORD':'PROJEKTprojekt##11',#Please provide the db password here
    #'HOST': 'localhost',
    #'PORT': '1521',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization/międzynarodowe standardy
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/
import os
STATIC_URL = '/static/'

STATICFILES_DIRS = (
  os.path.join(BASE_DIR, 'static'),
)
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

def get_cursor():
    userpwd = "PROJEKTprojekt##11"  # Obtain password string from a user prompt or environment variable
    connection = cx_Oracle.connect(user="ADMIN", password=userpwd,
                                   dsn="db202112131719_high",
                                   encoding="UTF-8")
    return connection.cursor()

def get_table(tablename, condition = None):
    cursor = get_cursor()
    try:
        if not condition:
            result = [a for a in cursor.execute("select * from "+tablename)]
            return result
        else:

            result = [a for a in cursor.execute("select * from " + tablename+ " where "+ condition)]
            return result

    except:
        return 0