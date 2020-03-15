import os

from quaddicted.settings.common import *

DEBUG = False
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'quaddicted',
		'USER': 'quaddicted',
		'PASSWORD': 'quaddicted',
		'HOST': 'localhost',
		'PORT': '5432',
	}
}

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'handlers': {
		'console': {
			'class': 'logging.StreamHandler',
		},
	},
	'loggers': {
		'django': {
			'handlers': ['console'],
			'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR'),
		},
	},
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = '/srv/www/quaddicted/static'
STATICFILES_DIRS = [
	os.path.join(BASE_DIR, 'quaddicted', 'static'),
]

# Save all uploads to the project directory during development
MEDIA_URL = '/media/'
MEDIA_ROOT = '/srv/www/quaddicted/media'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
