from django.contrib import admin

from lukeblog.base_admin import BaseOwnerAdmin  # 导入admin中共有的配置，本文件中的admin类应当继承于此类
from lukeblog.custom_site import custom_site  # 导入admin页面定制site

from .models import Link, SideBar


@admin.register(Link, site=custom_site)
class LinkAdmin(BaseOwnerAdmin):
    list_display = ('title', 'href', 'status', 'weight', 'created_time')
    fields = ('title', 'href', 'status', 'weight')


@admin.register(SideBar, site=custom_site)
class SideBarAdmin(BaseOwnerAdmin):
    list_display = ('title', 'display_type', 'content', 'created_time')
    fields = ('title', 'display_type', 'content')
