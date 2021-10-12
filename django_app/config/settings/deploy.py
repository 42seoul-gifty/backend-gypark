from .base import *


DEPLOY_SECRET = json.loads(SECRET_DEPLOY_FILE.read_text())

DEBUG = DEPLOY_SECRET['debug']

ALLOWED_HOSTS = DEPLOY_SECRET['allowed_hosts']

WSGI_APPLICATION = 'config.wsgi.deploy.application'

DATABASES = {'default': DEPLOY_SECRET['databases']}

STATIC_ROOT = BASE_DIR / 'staticfiles'
