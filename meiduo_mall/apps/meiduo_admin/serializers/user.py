from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'mobile', 'email']
        extra_kwargs = {
            'username': {
                'max_length': 20,
                'min_length': 5
            },
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': True
            }
        }

    # def validate(self, attrs):
    #     username = attrs.get('username')
    #     if User.objects.filter(username=username):
    #         raise serializers.ValidationError('用户名已存在')
    #     return attrs

    def create(self, validated_data):
        """设置入库密码加密保存"""
        return User.objects.create_user(**validated_data)