from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.meiduo_admin.user import meiduo_token
from apps.meiduo_admin.views.brand import BrandAPIViewSet
from apps.meiduo_admin.views.home import DailyActiveAPIView, DailyOrderCountAPIView, \
    UserCountAPIView, DailyUserIncreAPIView, MonthUserIncreAPIView
from apps.meiduo_admin.views.image import ImageAPIViewSet, ImageSKUAPIView
from apps.meiduo_admin.views.order import OrderInfoAPIView, OrderDetailAPIView, OrderStatusAPIView
from apps.meiduo_admin.views.permissions import PermissionAPIViewSet, ContentTypeAPIView, GroupAPIViewSet, \
    GroupPermissionListAPIView, AdminAPIViewSet
from apps.meiduo_admin.views.sku import SKUAPIViewSet, GoodsCategoryAPIView, SPUListAPIView, SUPSpecView
from apps.meiduo_admin.views.specs import SpecAPIViewSet
from apps.meiduo_admin.views.specs_options import SpecListAPIView, Spec_optionAPIViewSet
from apps.meiduo_admin.views.spu import SPUAPIViewSet, BrandAPIView, CategoryOneAPIView, CategoryOtherAPIView
from apps.meiduo_admin.views.user import UserAPIView

urlpatterns = [
    # login
    path('authorizations/', meiduo_token),
    # home
    path('statistical/day_active/', DailyActiveAPIView.as_view()),
    path('statistical/day_orders/', DailyOrderCountAPIView.as_view()),
    path('statistical/total_count/', UserCountAPIView.as_view()),
    path('statistical/day_increment/', DailyUserIncreAPIView.as_view()),
    path('statistical/month_increment/', MonthUserIncreAPIView.as_view()),
    # user
    path('users/', UserAPIView.as_view()),
    # order
    path('orders/<order_id>/status/', OrderStatusAPIView.as_view()),
    path('orders/<pk>/', OrderDetailAPIView.as_view()),
    path('orders/', OrderInfoAPIView.as_view()),
    # image 查询所有sku
    path('skus/simple/', ImageSKUAPIView.as_view()),
    # sku 三级分类数据、spu、spu规格
    path('skus/categories/', GoodsCategoryAPIView.as_view()),
    path('goods/simple/', SPUListAPIView.as_view()),
    path('goods/<pk>/specs/', SUPSpecView.as_view()),
    # spu 获取品牌数据\一级分类、二三级分类
    path('goods/brands/simple/', BrandAPIView.as_view()),
    path('goods/channel/categories/', CategoryOneAPIView.as_view()),
    path('goods/channel/categories/<pk>/', CategoryOtherAPIView.as_view()),
    # options 中规格名称列表、规格选项的详情信息
    path('goods/specs/simple/', SpecListAPIView.as_view()),
    # path('specs/options/<pk>/', Spec_Option_RetrieveAPIView.as_view()),

    # 权限中获取contentype
    path('permission/content_types/', ContentTypeAPIView.as_view()),
    # 组中获取权限列表
    path('permission/simple/', GroupPermissionListAPIView.as_view()),
    path('permission/groups/simple/', GroupPermissionListAPIView.as_view()),
]

router = DefaultRouter()
# skuimage
router.register('skus/images', ImageAPIViewSet, basename='images')
# sku
router.register('skus', SKUAPIViewSet, basename='skus')
# specs
router.register('goods/specs', SpecAPIViewSet, basename='specs')
# specs_option
router.register('specs/options', Spec_optionAPIViewSet, basename='specs_options')
# brand
router.register('goods/brands', BrandAPIViewSet, basename='brand')
# spu
router.register('goods', SPUAPIViewSet, basename='spu')
# permission
router.register('permission/perms', PermissionAPIViewSet, basename='permission')
# permission group
router.register('permission/groups', GroupAPIViewSet, basename='group')
# admin
router.register('permission/admins', AdminAPIViewSet, basename='admin')
urlpatterns += router.urls
