from datetime import date

from django.core.cache import cache

from django.db.models import Q, F  # Q解决关键字搜索...or...的问题, F解决数据库原子查询
from django.views.generic import DetailView, ListView
from django.shortcuts import get_object_or_404

from config.models import SideBar
from comment.models import Comment
from comment.forms import CommentForm

from .models import Post, Tag, Category


class CommonViewMixin:
    """ 通用功能视图 """
    def get_context_data(self, **kwargs):
        """ 通过重写该方法(所有类视图都继承该方法)可以[增加]视图的上下文键值对，后面的类视图与这里一样用法，共3步 """
        # 第1步：获取父类中的数据
        context = super().get_context_data(**kwargs)
        # 第2步：增加新键值对
        context.update({
            'sidebars': SideBar.get_all(),  # 侧边栏功能
        })
        context.update(Category.get_navs())  # 导航功能
        # 第3步：返回新的数据
        return context


class IndexView(CommonViewMixin, ListView):
    """ 通用索引视图 """
    queryset = Post.latest_posts()  # 与Model属性二选一，queryset有过滤功能
    paginate_by = 3  # 每页的数量
    # 如果不设置这里的'post_list'，在模板中该变量就变成默认的'object_list'
    context_object_name = 'post_list'  # 体现在模板中的 {% for post in post_list %}
    template_name = 'blog/list.html'  # 模板所在位置


class CategoryView(IndexView):
    """ 分类列表视图 """
    def get_context_data(self, **kwargs):
        """ 再次重写该方法，最终目的为了向模板增加新的上下文"category" """
        context = super().get_context_data(**kwargs)
        # kwargs实际上就是从URL传来的参数字典
        category_id = self.kwargs.get('category_id')
        # 获取对应id的Category实例
        category = get_object_or_404(Category, pk=category_id)
        context.update({
            'category': category,  # 将对应id的Category实例增加到模板的上下文
        })
        return context

    def get_queryset(self):
        """ 重写该方法，相当于改写了queryset属性，用于实现分类过滤 """
        # 第1步：复制取得父类的queryset，在这里，取得的是父类IndexView中的全部最新文章的QuerySet
        queryset = super().get_queryset()
        # 第2步：这里用到了字典的get()方法，取得URL中的参数值，用以QuerySet的过滤操作
        category_id = self.kwargs.get('category_id')
        # 第3步：返回过滤的QuerySet对象
        return queryset.filter(category__id=category_id)


class TagView(IndexView):
    """ Tag列表视图 """
    def get_context_data(self, **kwargs):
        """ 再次重写该方法，最终目的为了向模板增加新的上下文"tag" """
        context = super().get_context_data(**kwargs)
        tag_id = self.kwargs.get('tag_id')
        tag = get_object_or_404(Tag, pk=tag_id)
        context.update({
            'tag': tag,
        })
        return context

    def get_queryset(self):
        """ 重写该方法，相当于改写了queryset属性，用于实现分类过滤 """
        queryset = super().get_queryset()
        tag_id = self.kwargs.get('tag_id')
        return queryset.filter(tag__id=tag_id)


class SearchView(IndexView):
    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'keyword': self.request.GET.get('keyword')
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.GET.get('keyword')
        if not keyword:
            return queryset
        # icontains是忽略大小写的字段查询
        return queryset.filter(Q(title__icontains=keyword) | Q(desc__icontains=keyword))


class AuthorView(IndexView):
    def get_context_data(self, **kwargs):
        """ 在返回的页面中增加用户名的显示 """
        context = super().get_context_data(**kwargs)
        author_id = self.kwargs.get('owner_id')
        from django.contrib.auth.models import User
        author_name = User.objects.get(id=author_id)  # 根据用户id获取用户名
        context.update({
            'author_name': author_name
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        author_id = self.kwargs.get('owner_id')
        return queryset.filter(owner_id=author_id)


class PostDetailView(CommonViewMixin, DetailView):
    queryset = Post.latest_posts()
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'  # 设置查询的主键名称（与URLconfig的尖括号中一致）

    def get(self, request, *args, **kwargs):
        """ 重写get方法，增加pv和uv的统计 """
        response = super().get(request, *args, **kwargs)
        self.handle_visited()
        return response

    def handle_visited(self):
        """ 在访问文章后增加pv和uv的方法 """
        increase_pv = False
        increase_uv = False
        uid = self.request.uid
        pv_key = 'pv:%s:%s' % (uid, self.request.path)
        uv_key = 'uv:%s:%s:%s' % (uid, str(date.today()), self.request.path)

        if not cache.get(pv_key):
            increase_pv = True
            cache.set(pv_key, 1, 1*60)  # 1分钟有效

        if not cache.get(uv_key):
            increase_uv = True
            cache.set(uv_key, 1, 24*60*60)  # 24小时有效

        if increase_pv and increase_uv:
            Post.objects.filter(pk=self.object.id).update(pv=F('pv') + 1, uv=F('uv') + 1)
        elif increase_pv:
            Post.objects.filter(pk=self.object.id).update(pv=F('pv') + 1)
        elif increase_uv:
            Post.objects.filter(pk=self.object.id).update(uv=F('uv') + 1)
