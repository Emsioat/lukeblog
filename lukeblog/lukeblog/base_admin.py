from django.contrib import admin


class BaseOwnerAdmin(admin.ModelAdmin):
    """ 抽象出admin中共有的配置，重写相关admin.ModelAdmin中的一些方法 """
    exclude = ('owner', )  # 排除显示字段owner

    def get_queryset(self, request):
        """ 除非是超级管理员，否则只显示当前用户的对象（权限控制） """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        """
        用来自动补充文章、分类、标签、侧边栏、友连这些Model的owner字段
        :param request: 当前传入的请求
        :param obj: 当前要保存的对象
        :param form: 页面提交过来的表单对象
        :param change: 用于标志本次保存的数据是新增的还是更新的
        """
        # 设置模型中的owner字段为当前登录用户
        obj.owner = request.user
        return super().save_model(request, obj, form, change)
