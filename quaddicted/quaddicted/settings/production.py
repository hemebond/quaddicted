import os

from quaddicted.settings.common import *

DEBUG = False
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
