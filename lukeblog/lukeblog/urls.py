"""lukeblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# --- 库 ---
from django.urls import path, include
from django.contrib import admin
# import xadmin
# from xadmin.plugins import xversion  # version模块自动注册需要版本控制的 Model
import mgadmin
from mgadmin.plugins import xversion
from django.contrib.sitemaps import views as sitemap_views
from django.views.decorators.cache import cache_page  # Django的缓存模块

# 配置文件上传及访问路径(生产环境用Nginx完成)
from django.conf import settings
from django.conf.urls.static import static

# API路由库
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls

# --- View ---
from blog.views import (
    IndexView, CategoryView, TagView, PostDetailView, SearchView, AuthorView,
)
from blog.rss import LatestPostFeed
from blog.sitemap import PostSitemap
from blog.apis import PostViewSet, CategoryViewSet
from config.views import LinkListView
from comment.views import CommentView
from .custom_site import custom_site  # 自定义站点（admin）

# xadmin.autodiscover()
mgadmin.autodiscover()
xversion.register_models()  # version模块自动注册需要版本控制的 Model

# API路由
router = DefaultRouter()
router.register(r'post', PostViewSet, basename='api-post')  # 相当于设置PostViewSet的URL为/api/post
router.register(r'category', CategoryViewSet, basename='api-category')  # 相当于设置CategoryViewSet的URL为/api/category

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('category/<int:category_id>/', CategoryView.as_view(), name='category-list'),
    path('tag/<int:tag_id>/', TagView.as_view(), name='tag-list'),
    path('search/', SearchView.as_view(), name='search'),
    path('author/<owner_id>', AuthorView.as_view(), name='author'),
    path('post/<int:post_id>.html', PostDetailView.as_view(), name='post-detail'),
    path('rss/', LatestPostFeed(), name='rss'),
    # 缓存有三个参数，第一个表示缓存时间（这里缓存20分钟有效），cache="default"默认即为使用默认缓存，key_prefix表示缓存秘钥前缀字符串，本质是返回装饰器
    path('sitemap.xml', cache_page(60 * 20, key_prefix='sitemap_cache_')(sitemap_views.sitemap), {'sitemaps': {'posts': PostSitemap}}),
    path('comment/', CommentView.as_view(), name='comment'),
    path('links/', LinkListView.as_view(), name='links'),
    path('super_admin/', admin.site.urls, name='super-admin'),
    path('admin/', custom_site.urls, name='admin'),
    # path('xadmin/', xadmin.site.urls, name='xadmin'),
    path('mgadmin/', mgadmin.site.urls, name='mgadmin'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api/', include(router.urls)),
    path('api/docs/', include_docs_urls(title='lukeblog apis')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 如果开启Debug模式，则增加Django-Debug-Toolbar的URL配置
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
