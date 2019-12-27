from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin.models import LogEntry  # 查看日志

from lukeblog.base_admin import BaseOwnerAdmin  # 导入admin中共有的配置，本文件中的admin类应当继承于此类
from lukeblog.custom_site import custom_site  # 导入admin页面定制site

from .models import Category, Tag, Post  # 导入该App下的models.py中的模块
from .adminforms import PostAdminForm  # 导入自定义admin的form


class PostInline(admin.TabularInline):  # TabularInline为横向表排版，StackedInline为纵向排版
    """ 在[分类]中内置[编辑文章]的功能（通常适合字段较少的场景，这里仅作演示） """
    fields = ('title', 'desc')
    extra = 2  # 控制额外多几个（显示除了该分类下已有的文章，再显示多少个空行）
    model = Post  # 要内置编辑的模型


@admin.register(Category, site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):
    inlines = [PostInline, ]  # 在[分类]中内置[编辑文章]的功能（需定义PostInline类）
    list_display = ('name', 'status', 'is_nav', 'post_count', 'created_time')  # 在admin列表中要展示的字段
    fields = ('name', 'status', 'is_nav')  # 在admin编辑页面要展示的字段

    def post_count(self, obj):
        """ 在列表页增加一个[文章总数]的自定义字段 """
        return obj.post_set.count()

    # 设置自定义字段函数，在列表页表头中显示的名称
    post_count.short_description = '文章总数'


@admin.register(Tag, site=custom_site)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'created_time')
    fields = ('name', 'status')


class CategoryOwnerFilter(admin.SimpleListFilter):
    """ 自定义过滤器只展示当前用户分类(用于文章列表右侧) """
    title = '文章列表过滤'  # 显示在文章列表右侧的过滤器名称(页面可见的名称)
    parameter_name = 'owner_category'  # 将在URL查询中使用的参数名

    def lookups(self, request, model_admin):
        """ 该方法需要返回一个元组列表，用于生成HTML，格式为[(URL参数, 页面显示在过滤器中的名称), ...] """
        # QuerySet的链式调用（Model.objects.filter支持链式，values_list不支持，后者返回类似<QuerySet[(id, '名称'), ...]>
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        """ 定义根据lookups方法中定义的URL参数，页面返回的数据 """
        # self.value()即为取得的URL请求参数，如：页面为?owner_category=1，则此处值为1
        category_id = self.value()
        if category_id:
            # QuerySet为列表所有数据的合集，即post的数据集，在这里进行过滤显示
            return queryset.filter(category__id=category_id)
        return queryset


@admin.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    form = PostAdminForm  # 将默认form改为自定义的form（在头部引入）
    list_display = ['title', 'category', 'status', 'created_time', 'owner', 'operator']
    list_display_links = []  # 配置哪些字段可以作为链接，点击进入编辑页，设为None，则不配置任何可点击字段。

    # list_filter = ['category', ]  # 配置页可根据category中的字段进行过滤显示（显示在文章列表的右侧，有一个过滤器）
    list_filter = [CategoryOwnerFilter]  # 自定义文章列表右侧的过滤器（需要定义CategoryOwnerFilter类）
    search_fields = ['title', 'category__name']  # 配置搜索字段（搜索结果为文章标题字段、category中的name字段）

    # 是否在顶部or底部展示动作相关配置
    actions_on_top = True
    actions_on_bottom = True

    # ---- 以下为编辑页面的配置 ----

    save_on_top = True  # 顶部操作按钮

    # fieldsets可以代替fields，来自定义布局格式，最内层字典的key可以是fields、description、classes，
    # classes默认有collapse(折叠)/wide或自定义
    fieldsets = (
        ('基础配置', {
            'description': '基础配置描述',
            'fields': (
                ('title', 'category'),
                'status',
            ),
        }),
        ('内容', {
            'fields': (
                'desc',
                'content',
            ),
        }),
        ('额外信息', {
            'classes': ('collapse', ),
            'fields': ('tag', ),
        }),
    )

    # 效果为"可用的标签" -> "选中的标签"(用此配置的字段必须是many-to-many的字段,否则报错)
    filter_horizontal = ('tag', )  # 水平横向显示
    # filter_vertical = ('tag', )  # 垂直纵向显示

    def operator(self, obj):
        """ 在列表页增加一个[操作]自定义字段，功能为[编辑]，将此方法名加入到list_display中即可展示 """
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('cus_admin:blog_post_change', args=(obj.id,))
        )

    # 设置自定义字段函数，在列表页表头中显示的名称
    operator.short_description = '操作'

    class Media:
        """ 引入自定义css和js """
        '''css = {
            'all': ("https://cdn.bootcss.com/twitter-bootstrap/4.3.1/css/bootstrap.min.css", ),
        }'''
        js = ('https://cdn.bootcss.com/twitter-bootstrap/4.3.1/js/bootstrap.bundle.js', )


@admin.register(LogEntry, site=custom_site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['object_repr', 'object_id', 'action_flag', 'user', 'change_message']
