from .base import *  # NOQA


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 在base基础上增加的App
INSTALLED_APPS += [
    # 'debug_toolbar',  # Django-Debug-Toolbar模块
]

# 在base基础上增加的中间件
MIDDLEWARE += [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',  # Django-Debug-Toolbar中间件
]

INTERNAL_IPS = ['127.0.0.1', ]  # Django-Debug-Toolbar在本机调试

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, '../../db.sqlite3'),
    }
}
