from quaddicted.settings.common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xj2&3&xj@$zz5va@^2si$ei7%&q^i(x*3(9%u04ew=4$8*5ziv'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# DATABASES = {
# 	'default': {
# 		'ENGINE': 'django.db.backends.postgresql',
# 		'NAME': 'quaddicted',
# 		'USER': 'quaddicted',
# 		'PASSWORD': 'quaddicted',
# 		'HOST': 'localhost',
# 		'PORT': '5432',
# 	}
# }


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
			'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
		},
	},
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'quaddicted', 'static'),
]

# Save all uploads to the project directory during development
MEDIA_URL = '/media/'
MEDIA_ROOT = '/srv/www/quaddicted/media'
