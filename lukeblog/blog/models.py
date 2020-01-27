import mistune  # 将Markdown转换为Html的第三方库

from django.utils.functional import cached_property  # 将方法返回的值缓存成实例的属性（装饰器）
from django.contrib.auth.models import User
from django.db import models
from django.core.cache import cache  # 热门文章缓存


class Category(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )

    name = models.CharField(max_length=50, verbose_name="名称")
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name="状态")
    is_nav = models.BooleanField(default=False, verbose_name="是否为导航")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="作者")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    @classmethod
    def get_navs(cls):
        """ 根据is_nav判断导航显示位置 """
        categories = cls.objects.filter(status=cls.STATUS_NORMAL)
        nav_categories = []
        normal_categories = []
        for cate in categories:
            if cate.is_nav:
                nav_categories.append(cate)
            else:
                normal_categories.append(cate)

        return {
            'navs': nav_categories,
            'categories': normal_categories,
        }

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = verbose_name_plural = '分类'


class Tag(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )

    name = models.CharField(max_length=10, verbose_name="名称")
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name="状态")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="作者")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = verbose_name_plural = '标签'


class Post(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_DRAFT = 2
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
        (STATUS_DRAFT, '草稿'),
    )

    title = models.CharField(max_length=255, verbose_name="标题")
    desc = models.CharField(max_length=1024, blank=True, verbose_name="摘要")
    content = models.TextField(verbose_name="正文", help_text="正文必须为MarkDown格式")
    content_html = models.TextField(verbose_name="正文html代码", blank=True, editable=False)  # 自动转换HTML代码，不可人为编辑
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name="状态")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="分类")
    tag = models.ManyToManyField(Tag, verbose_name="标签")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="作者")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_md = models.BooleanField(default=False, verbose_name="使用MarkDown语法")
    pv = models.PositiveIntegerField(default=1)
    uv = models.PositiveIntegerField(default=1)

    @cached_property  # 将方法返回的值缓存成实例的属性
    def tags(self):
        return ','.join(self.tag.values_list('name', flat=True))

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """ 重写save方法，在保存内容前进行一些操作 """
        # 判断是否使用MarkDown语法进行编辑，来确定内容保存方式
        if self.is_md:
            self.content_html = mistune.markdown(self.content)  # 转换Markdown格式并替换content_html的内容
        else:
            self.content_html = self.content  # 如果不是选用MarkDown，则使用富文本编辑器直接转换为HTML，所以这里不作转换
        super().save()

    @staticmethod
    def get_by_tag(tag_id):
        """ 根据tag_id获取文章列表 """
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            tag = None
            post_list = []
        else:  # try执行成功则执行这里
            # 返回根据tag_id过滤的文章列表，select_related为了避免N+1问题，之后可通过先遍历post_list，再用post.owner这样来访问数据
            post_list = tag.post_set.filter(status=Post.STATUS_NORMAL).select_related('owner', 'category')

        return post_list, tag

    @staticmethod
    def get_by_category(category_id):
        """ 根据category_id获取文章列表，与之前的tag_id获取列表的逻辑一致 """
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            category = None
            post_list = []
        else:
            post_list = category.post_set.filter(status=Post.STATUS_NORMAL).select_related('owner', 'category')

        return post_list, category

    @classmethod
    def latest_posts(cls, with_related=True):
        """ 增加自定义参数with_related，如果是True，则一次性查询post表和关联的外键，避免N+1问题；而不需要外键数据展示的模板，可以传入False """
        queryset = cls.objects.filter(status=cls.STATUS_NORMAL)
        if with_related:
            queryset = queryset.select_related('owner', 'category')  # 一次性额外查询，避免N+1
        return queryset

    @classmethod
    def hot_posts(cls):
        """ 根据pv排序热门文章 """
        result = cache.get('hot_posts')  # 尝试从缓存读取热门文章数据
        if not result:
            result = cls.objects.filter(status=cls.STATUS_NORMAL).order_by('-pv')
            cache.set('hot_posts', result, 10 * 60)  # 将数据存入缓存
        return result

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = verbose_name_plural = '文章'
        ordering = ['-id']  # 根据id进行降序排列
