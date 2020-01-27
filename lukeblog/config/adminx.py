import xadmin

from lukeblog.base_xadmin import BaseOwnerXadmin  # 导入admin中共有的配置，本文件中的admin类应当继承于此类

from .models import Link, SideBar


@xadmin.sites.register(Link)
class LinkAdmin(BaseOwnerXadmin):
    list_display = ('title', 'href', 'status', 'weight', 'created_time')
    fields = ('title', 'href', 'status', 'weight')


# xadmin.site.register(Link, LinkAdmin)  # 注册传入Model, AdminView


@xadmin.sites.register(SideBar)
class SideBarAdmin(BaseOwnerXadmin):
    list_display = ('title', 'display_type', 'content', 'created_time')
    fields = ('title', 'display_type', 'content')


# xadmin.site.register(SideBar, SideBarAdmin)  # 注册传入Model, AdminView
