class BaseOwnerMgadmin:
    """ 抽象出admin中共有的配置，重写相关admin.ModelAdmin中的一些方法 """
    exclude = ('owner', )  # 排除显示字段owner

    def get_list_queryset(self):
        """ 除非是超级管理员，否则只显示当前用户的对象（权限控制） """
        request = self.request
        qs = super().get_list_queryset()
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def save_models(self):
        """
        用来自动补充文章、分类、标签、侧边栏、友连这些Model的owner字段
        """
        # 设置模型中的owner字段为当前登录用户
        self.new_obj.owner = self.request.user
        return super().save_models()
