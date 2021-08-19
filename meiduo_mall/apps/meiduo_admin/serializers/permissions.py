from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from apps.users.models import User


class PermissionSerializer(serializers.ModelSerializer):
    """权限"""
    class Meta:
        model = Permission
        fields = '__all__'


class ContentTypeSerializer(serializers.ModelSerializer):
    """权限类型"""
    class Meta:
        model = ContentType
        fields = ['id', 'name']


class GroupSerializer(serializers.ModelSerializer):
    """管理组"""
    class Meta:
        model = Group
        fields = '__all__'


class AdminSerializer(serializers.ModelSerializer):
    """管理员"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email', 'password', 'groups', 'user_permissions']
        extra_kwargs = {
            'group': {'write_only': True},
            'user_permission': {'write_only': True},
        }

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data.get('password'))
        user.is_staff = True
        user.save()
        return user

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        password = validated_data.get('password')
        if password is not None:
            instance.set_password(password)
            instance.save()
        return instance

