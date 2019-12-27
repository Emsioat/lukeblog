from django.contrib import admin

from lukeblog.base_admin import BaseOwnerAdmin  # 导入admin中共有的配置，本文件中的admin类应当继承于此类
from lukeblog.custom_site import custom_site  # 导入admin页面定制site

from .models import Comment


@admin.register(Comment, site=custom_site)
class CommentAdmin(BaseOwnerAdmin):
    list_display = ('target', 'nickname', 'content', 'website', 'created_time')
    fields = ('target', 'nickname', 'content', 'website', 'email', 'status')
