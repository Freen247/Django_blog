"""django_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path

from apps.blog import views as blog_views
from django.conf.urls import include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import xadmin

from django.contrib import admin

#网站地图
from django.contrib.sitemaps.views import sitemap
from apps.blog.sitemaps import ArticleSitemap, CategorySitemap
#网站地图


sitemaps = {
    'articles': ArticleSitemap,
    'categories': CategorySitemap
}
xadmin.autodiscover()

# version模块自动注册需要版本控制的 Model
from xadmin.plugins import xversion
xversion.register_models()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    path('mdeditor/', include('mdeditor.urls')),  # Django-mdeditor URLS
     # index
    path('', include('apps.blog.urls'), name='blog'),
    #用户

    path('accounts/', include('allauth.urls'), name='accounts'),
    path('accounts/', include('apps.user.urls'), name='accounts'),
    #评论
    path('comment/', include('apps.comment.urls'), name = 'comment'),
    #工具
    path('md2html/', blog_views.md2html, name='markdown'),
    #网站地图
    path('sitemap.xml/', sitemap, {'sitemaps':sitemaps}, name = 'django.contrib.sitemaps.views.sitemap'),
]
# tools

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)