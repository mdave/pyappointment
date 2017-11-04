from jsonconfigparser import JSONConfigParser
import os, json

##
## Set up Django application settings
##

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    'bootstrapform',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pyappointment.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ 'pyappointment/templates' ],
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

WSGI_APPLICATION = 'pyappointment.wsgi.application'

# Static file collection

STATIC_ROOT = os.path.join(BASE_DIR, "static_collect")

STATICFILES_DIRS = [
    # Copy bootstrap assets.
    ('fonts', os.path.join(BASE_DIR, "node_modules", "bootstrap", "fonts")),
    ('less', os.path.join(BASE_DIR, "node_modules", "bootstrap", "less")),
    ('bootstrap-js', os.path.join(BASE_DIR, "node_modules", "bootstrap", "js")),
    # Copy other assets.
    ('less', os.path.join(BASE_DIR, "pyappointment", "static", "less")),
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_ENABLED = True
COMPRESS_PRECOMPILERS = (
    ('text/less', '/usr/local/bin/lessc {infile} {outfile}'),
)

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

##
## Import site-specifc stuff from config.ini.
##

config = JSONConfigParser()
config.read(os.path.join(BASE_DIR, "config.ini"))

# Django [django] block
SECRET_KEY = config.get('django', 'SECRET_KEY')
ALLOWED_HOSTS = config.get('django', 'ALLOWED_HOSTS')
DEBUG = config.get('django', 'DEBUG')
ADMINS = config.get('django', 'ADMINS')

# Parse meeting types
ORGANIZER_NAME = config.get('meetings', 'ORGANIZER_NAME')
ORGANIZER_EMAIL = config.get('meetings', 'ORGANIZER_EMAIL')
ORGANIZER_GREETING = config.get('meetings', 'ORGANIZER_GREETING')
BOOKING_TYPES = config.get('meetings', 'BOOKING_TYPES')

# Email settings
EMAIL_USE_SSL = config.get('email', 'USE_SSL')
EMAIL_ADDRESS = config.get('email', 'ADDRESS')
EMAIL_HOST = config.get('email', 'HOST')
EMAIL_PORT = config.get('email', 'PORT')
EMAIL_HOST_USER = config.get('email', 'HOST_USER')
EMAIL_HOST_PASSWORD = config.get('email', 'HOST_PASSWORD')

# Cronofy settings
CRONOFY_ACCESS_TOKEN = config.get('cronofy', 'ACCESS_TOKEN')

# Calendar names
CAL_NAMES = config.get("calendar", "CHECK")
CAL_CREATE_BOOKING = config.get("calendar", "BOOK")
TIME_ZONE = config.get("calendar", "TIME_ZONE")

# Parse availability strings
AVAIL_CONFIG_STRINGS = [
    config.get('availability', day) for day in (
        'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN')
]
