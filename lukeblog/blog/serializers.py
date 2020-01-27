""" RESTful（API）的序列化参数配置（序列化类似于表单格式）,这部分有点类似ModelForm,将这里的配置交给apis.py（相当于View层） """
from rest_framework import serializers
from rest_framework import pagination  # 为分类下显示文章列表提供页码功能

from .models import Post, Category


class PostSerializer(serializers.ModelSerializer):
    """ 文章列表的API序列化参数配置 """
    url = serializers.HyperlinkedIdentityField(view_name='api-post-detail')

    category = serializers.SlugRelatedField(
        read_only=True,  # 外键是否可写
        slug_field='name'  # 要显示的字段
    )

    tag = serializers.SlugRelatedField(
        many=True,  # 是否为多对多字段
        read_only=True,
        slug_field='name'
    )

    owner = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    created_time = serializers.DateTimeField(format='%y-%m-%d %H:%M:%S')

    class Meta:
        model = Post
        fields = ['url', 'id', 'title', 'category', 'tag', 'owner', 'created_time']


class PostDetailSerializer(PostSerializer):
    """ 文章详情页的API序列化参数配置 """
    class Meta:
        model = Post
        fields = ['id', 'title', 'category', 'tag', 'owner', 'content_html', 'created_time']  # 详情页多了content_html字段


class CategorySerializer(serializers.ModelSerializer):
    """ 分类数据的API序列化参数配置 """
    class Meta:
        model = Category
        fields = (
            'id', 'name', 'created_time',
        )


class CategoryDetailSerializer(CategorySerializer):
    """ 分类下显示文章列表，并显示页码的序列化配置 """
    # posts为最终展现的字段（加入Meta的fields中），这里用SerializerMethodField方法映射到paginated_posts方法上，实际用的数据来自
    # 后者返回的字典（包含关联该分类的文章列表、页码）
    posts = serializers.SerializerMethodField('paginated_posts')

    def paginated_posts(self, obj):  # 固定写法，obj为当前的[分类]对象
        posts = obj.post_set.filter(status=Post.STATUS_NORMAL)  # 关联模型小写_set表示当前关联对象的列表，即该分类下的文章列表
        paginator = pagination.PageNumberPagination()  # 分页工具
        page = paginator.paginate_queryset(posts, self.context['request'])
        serializer = PostSerializer(page, many=True, context={'request': self.context['request']})
        return {
            'count': posts.count(),
            'results': serializer.data,
            'previous': paginator.get_previous_link(),
            'next': paginator.get_next_link(),
        }

    class Meta:
        model = Category
        fields = ['id', 'name', 'created_time', 'posts']
