from .base import *


DEBUG_SECRET = json.loads(SECRET_DEBUG_FILE.read_text())

DEBUG = True

ALLOWED_HOSTS = DEBUG_SECRET['allowed_hosts']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

WSGI_APPLICATION = 'config.wsgi.debug.application'
