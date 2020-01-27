import xadmin

from lukeblog.base_xadmin import BaseOwnerXadmin  # 导入admin中共有的配置，本文件中的admin类应当继承于此类

from .models import Comment


@xadmin.sites.register(Comment)
class CommentAdmin(BaseOwnerXadmin):
    list_display = ('target', 'status', 'nickname', 'content', 'website', 'created_time')
    fields = ('target', 'nickname', 'content', 'website', 'email', 'status')


# xadmin.site.register(Comment, CommentAdmin)  # 注册传入Model, AdminView
