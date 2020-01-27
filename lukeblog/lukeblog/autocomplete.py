from dal import autocomplete

from blog.models import Category, Tag


class CategoryAutocomplete(autocomplete.Select2QuerySetView):
    """ 添加/修改文章时，填写分类自动补全 """
    def get_queryset(self):
        if not self.request.user.is_authenticated:  # 如果用户未登录
            return Category.objects.none()  # 不可以返回None，因为其他类还要处理QuerySet对象

        qs = Category.objects.filter(owner=self.request.user)  # 先取得当前用户下的所有分类

        if self.q:  # q为URL传来的参数
            qs = qs.filter(name__istartswith=self.q)
        return qs


class TagAutocomplete(autocomplete.Select2QuerySetView):
    """ 添加/修改文章时，填写Tag自动补全,逻辑同CategoryAutocomplete """
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Tag.objects.none()

        qs = Tag.objects.filter(owner=self.request.user)

        if self.q:
            qs = qs.filter(name__istartswith=self.q)
        return qs
