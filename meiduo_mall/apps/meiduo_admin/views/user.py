"""
用户管理视图
"""

from rest_framework.generics import ListAPIView, ListCreateAPIView

from apps.meiduo_admin.serializers.user import UserSerializer
from apps.meiduo_admin.utils import PageNum
from apps.users.models import User


class UserAPIView(ListCreateAPIView):
    """用户查询和创建"""
    serializer_class = UserSerializer
    pagination_class = PageNum

    def get_queryset(self):
        # 获取前端传递的keyword值
        keyword = self.request.query_params.get('keyword')
        # 如果keyword是空字符，则说明要获取所有用户数据
        if keyword is '' or keyword is None:
            return User.objects.all()
        else:
            return User.objects.filter(username__contains=keyword)

