""" API接口的View层（序列化配置来自serializers.py，数据来自QuerySet对象） """
from rest_framework import viewsets  # 更抽象的View
# from rest_framework.permissions import IsAdminUser  # 权限许可

from .models import Post, Category
from .serializers import PostSerializer, PostDetailSerializer, CategorySerializer, CategoryDetailSerializer


class PostViewSet(viewsets.ReadOnlyModelViewSet):  # 只读，若需写入，应继承自viewsets.ModelViewSet
    """ 文章列表及详情页API接口（DocString） """
    serializer_class = PostSerializer  # 这里的序列化参数里没有content_html字段（即正文），用于显示文章列表
    queryset = Post.objects.filter(status=Post.STATUS_NORMAL)

    # permission_classes = [IsAdminUser]  # 写入时的权限校验,并在客户端增加CSRF_TOKEN的获取

    def retrieve(self, request, *args, **kwargs):
        """ 文章详情页的API接口(对应前端Post Instance) """
        # 通过覆写父类中的serializer_class，改变详情页序列化参数（位于serializers.py），以增加字段content_html
        self.serializer_class = PostDetailSerializer
        return super().retrieve(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        """ 获取某个分类下的文章列表的接口 """
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ 分类数据API接口（DocString） """
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(status=Category.STATUS_NORMAL)

    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = CategoryDetailSerializer
        return super().retrieve(request, *args, **kwargs)
