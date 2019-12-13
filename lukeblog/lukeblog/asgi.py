"""
ASGI config for lukeblog project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

profile = os.environ.get('LUKEBLOG_PROFILE', 'develop')  # 获取系统变量值，默认为develop
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lukeblog.settings.%s' % profile)  # 自动适配开发环境或生产环境

application = get_asgi_application()
