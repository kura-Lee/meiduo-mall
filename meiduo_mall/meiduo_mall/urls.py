"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from utils.converters import UsernameConvert, MobileConvert
from django.urls import register_converter
#注册转换器
register_converter(UsernameConvert, 'username')
register_converter(MobileConvert, 'mobile')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.users.urls')),
    path('', include('apps.verifications.urls')),
    path('', include('apps.oauth.urls')),
    path('', include('apps.areas.urls')),
    path('', include('apps.goods.urls')),
    path('', include('apps.contents.urls')),
    path('', include('apps.carts.urls')),
    path('', include('apps.orders.urls')),
    path('', include('apps.pay.urls')),
    path('meiduo_admin/', include('apps.meiduo_admin.urls')),
    path('api-auth/', include('rest_framework.urls')),
]


