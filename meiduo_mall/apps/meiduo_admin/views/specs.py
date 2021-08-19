from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SPUSpecification
from apps.meiduo_admin.serializers.specs import SPUSpecSerializer
from apps.meiduo_admin.utils import PageNum


class SpecAPIViewSet(ModelViewSet):
    """SPUSpec信息"""
    queryset = SPUSpecification.objects.all()
    serializer_class = SPUSpecSerializer
    pagination_class = PageNum





