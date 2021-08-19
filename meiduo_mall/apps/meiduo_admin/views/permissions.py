from django.contrib.contenttypes.models import ContentType
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.serializers.permissions import PermissionSerializer, ContentTypeSerializer, GroupSerializer, \
    AdminSerializer
from apps.meiduo_admin.utils import PageNum
from django.contrib.auth.models import Permission, Group

from apps.users.models import User


class PermissionAPIViewSet(ModelViewSet):
    """权限管理"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = PageNum


class ContentTypeAPIView(ListAPIView):
    """所有权限类型查询"""
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer


class GroupAPIViewSet(ModelViewSet):
    """用户组"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = PageNum


class GroupPermissionListAPIView(ListAPIView):
    """用户组管理中获取权限列表"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class AdminAPIViewSet(ModelViewSet):
    """管路员视图集"""
    queryset = User.objects.filter(is_staff=True)
    serializer_class = AdminSerializer
    pagination_class = PageNum


class AdminGroupAPIView(ListAPIView):
    """管理员用户组展示"""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer





