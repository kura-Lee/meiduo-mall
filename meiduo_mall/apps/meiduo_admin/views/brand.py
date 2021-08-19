from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.serializers.brand import BrandSerializer
from apps.meiduo_admin.utils import PageNum
from apps.goods.models import Brand


class BrandAPIViewSet(ModelViewSet):
    """Brand"""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = PageNum


