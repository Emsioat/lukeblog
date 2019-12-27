""" 定制Site，URL指向的管理后台是admin.site，实际上是django.contrib.admin.AdminSite的一个实例 """
from django.contrib.admin import AdminSite


class CustomSite(AdminSite):
    """ 定制管理后台，URL实际指向的是AdminSite，因此我们继承这个类 """
    site_header = 'LukeBlog'  # 显示在admin页面左上角的LOGO
    site_title = 'LukeBlog管理后台'  # 在html的title中显示站点名称
    index_title = '首页'


custom_site = CustomSite(name='cus_admin')  # name用于使用django.urls.reverse获取URL地址时提供该实例
