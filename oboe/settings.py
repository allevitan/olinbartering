# Django settings for oboe project.

import dj_database_url
import os
import os.path

DEBUG = True
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = True

CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
		'LOCATION':'127.0.0.1:11211',
                'TIMEOUT': 1200000
	 }
}

#MAIL_BACKEND = 'django_ses.SESBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.us-east-1.amazonaws.com'
EMAIL_PORT = 25
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'AKIAJII2NPAE6AN5YJGA'
EMAIL_HOST_PASSWORD = 'ArEFaWJSSqTbR1GiwU+7067dNbpQ73BHXTIXx6XzybYA'

DEFAULT_FROM_EMAIL = 'olin.filtr@gmail.com'

AWS_ACCESS_KEY_ID = 'AKIAI45QD6OFLDQ47ZZA'
AWS_SECRET_ACCESS_KEY = 'abw8atzOBZ9oP8ZXwPiI+xtpWjmIBBFJX62Y3bhe'

AWS_STORAGE_BUCKET_NAME = 'oboe'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DIRNAME = os.path.dirname(__file__)

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

DATABASES = {
    'default': {
	'ENGINE': 'django.db.backends.sqlite3', # Add '', 'mysql', 'sqlite3' or 'oracle'.
	'NAME': 'devenvironment/testdatabase',                      # Or path to database file if using sqlite3.
	'USER': '',                      # Not used with sqlite3.
	'PASSWORD': '',                  # Not used with sqlite3.
	'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
	'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# if we're on the production server
if dj_database_url.config():
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG
    THUMBNAIL_DEBUG = True
    DATABASES['default'] = dj_database_url.config()
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    from memcacheify import memcacheify
    CACHES = memcacheify()
    CACHES['default']['TIMEOUT'] = 30000
    

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"\
#NOT USED with S3, so safe to keep in all the time
MEDIA_ROOT = os.path.join(DIRNAME, '../devenvironment/media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"

# ...
STATIC_ROOT = os.path.join(DIRNAME, 'static_media')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	os.path.join(DIRNAME, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'a!s-e8_iz=suy5^bzd@8idff(v7hl5^+k^$fkgbcf#gpc#1y4p'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	"oboe.context_processors.site_area",
	"oboe.context_processors.is_webkit",
        "oboe.context_processors.who_dis",
        "oboe.context_processors.the_folk",
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.core.context_processors.static",
	"django.contrib.messages.context_processors.messages")


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'oboe.LoginMiddleware.PreventAccess',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'oboe.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'oboe.wsgi.application'

TEMPLATE_DIRS = (
	os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
)

THUMBNAIL_ALIASES = {
    '': {
	'inlist': {'size': (64,64), 'crop': True}
	},
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'sorl.thumbnail',
    'oboe',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
	'require_debug_false': {
	    '()': 'django.utils.log.RequireDebugFalse'
	}
    },
    'handlers': {
	'mail_admins': {
	    'level': 'ERROR',
	    'filters': ['require_debug_false'],
	    'class': 'django.utils.log.AdminEmailHandler'
	}

    },
    'loggers': {
	'django.request': {
	    'handlers': ['mail_admins'],
	    'level': 'ERROR',
	    'propagate': True,
	},
    }
}
