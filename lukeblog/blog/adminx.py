from django.utils.html import format_html
import xadmin
from xadmin.layout import Row, Fieldset, Container  # xadmin的表单支持
from xadmin.filters import manager  # 自定义过滤器
from xadmin.filters import RelatedFieldListFilter  # 自定义过滤器基类（自定义过滤器继承于该类）

from lukeblog.base_xadmin import BaseOwnerXadmin  # 导入admin中共有的配置，本文件中的admin类应当继承于此类

from .models import Category, Tag, Post  # 导入该App下的models.py中的模块
from .adminforms import PostAdminForm  # 导入自定义admin的form


class PostInline:  # TabularInline为横向表排版，StackedInline为纵向排版
    # 在[分类]中内置[编辑文章]的功能（通常适合字段较少的场景，这里仅作演示）
    form_layout = (
        Container(
            Row("title", "desc"),
        )
    )
    extra = 2  # 控制额外多几个（显示除了该分类下已有的文章，再显示多少个空行）
    model = Post  # 要内置编辑的模型


@xadmin.sites.register(Category)
class CategoryAdmin(BaseOwnerXadmin):
    inlines = [PostInline, ]  # 在[分类]中内置[编辑文章]的功能（需定义PostInline类）
    list_display = ('name', 'status', 'is_nav', 'post_count', 'created_time')  # 在admin列表中要展示的字段
    fields = ('name', 'status', 'is_nav')  # 在admin编辑页面要展示的字段

    def post_count(self, obj):
        """ 在列表页增加一个[文章总数]的自定义字段 """
        return obj.post_set.count()

    # 设置自定义字段函数，在列表页表头中显示的名称
    post_count.short_description = '文章总数'


# xadmin.site.register(Category, CategoryAdmin)  # 注册传入Model, AdminView


@xadmin.sites.register(Tag)
class TagAdmin(BaseOwnerXadmin):
    list_display = ('name', 'status', 'created_time')
    fields = ('name', 'status')


# xadmin.site.register(Tag, TagAdmin)  # 注册传入Model, AdminView


class CategoryOwnerFilter(RelatedFieldListFilter):
    """ 自定义过滤器只展示当前用户分类(用于文章列表上方的"过滤器") """

    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        """ test方法作用是确认字段是否需要被当前的过滤器处理 """
        return field.name == 'category'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        # 重新获取lookup_choices，默认情况（父类中）是查询所有数据，在这里配置为根据owner过滤
        self.lookup_choices = Category.objects.filter(owner=request.user).values_list('id', 'name')


manager.register(CategoryOwnerFilter, take_priority=True)  # 注册到过滤器管理器中，并设置优先级


@xadmin.sites.register(Post)
class PostAdmin(BaseOwnerXadmin):
    form = PostAdminForm  # 将默认form改为自定义的form（在头部引入）
    list_display = ['title', 'category', 'status', 'created_time', 'owner', 'operator']
    list_display_links = []  # 配置哪些字段可以作为链接，点击进入编辑页，设为None，则不配置任何可点击字段。
    raw_id_fields = ('category',)

    # list_filter = ['category', ]  # 配置页可根据category中的字段进行过滤显示（显示在文章列表的右侧，有一个过滤器）
    list_filter = ['category']  # 自定义文章列表右侧的过滤器（需要定义CategoryOwnerFilter类）
    search_fields = ['title', 'category__name']  # 配置搜索字段（搜索结果为文章标题字段、category中的name字段）

    # 是否在顶部or底部展示动作相关配置
    actions_on_top = True
    actions_on_bottom = True

    # ---- 以下为编辑页面的配置 ----

    save_on_top = True  # 顶部操作按钮

    # fieldsets可以代替fields，来自定义布局格式，最内层字典的key可以是fields、description、classes，
    # classes默认有collapse(折叠)/wide或自定义
    form_layout = (
        Fieldset(
            '基础信息',
            Row("title", "category"),
            'status',
            'tag',
        ),
        Fieldset(
            '内容信息',
            'desc',
            'is_md',
            'content_ck',
            'content_md',
            'content',
        ),
    )

    # 效果为"可用的标签" -> "选中的标签"(用此配置的字段必须是many-to-many的字段,否则报错)
    filter_horizontal = ('tag',)  # 水平横向显示

    # filter_vertical = ('tag', )  # 垂直纵向显示

    def operator(self, obj):
        """ 在列表页增加一个[操作]自定义字段，功能为[编辑]，将此方法名加入到list_display中即可展示 """
        return format_html(
            '<a href="{}">编辑</a>',
            self.model_admin_url('change', obj.id)
        )

    # 设置自定义字段函数，在列表页表头中显示的名称
    operator.short_description = '操作'


# xadmin.site.register(Post, PostAdmin)  # 注册传入Model, AdminView
