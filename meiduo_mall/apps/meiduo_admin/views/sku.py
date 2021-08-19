from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SKU, GoodsCategory, SPU, SPUSpecification
from apps.meiduo_admin.serializers.sku import SKUSerializer, GoodsCategorySerializer, SPUListSerializer, \
    SPUSpecSerializer
from apps.meiduo_admin.utils import PageNum


class SKUAPIViewSet(ModelViewSet):

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return SKU.objects.filter(name__contains=keyword)
        return SKU.objects.all()
    serializer_class = SKUSerializer
    pagination_class = PageNum



class GoodsCategoryAPIView(ListAPIView):
    """三级分类数据查询"""

    queryset = GoodsCategory.objects.filter(subs=None)
    serializer_class = GoodsCategorySerializer


class SPUListAPIView(ListAPIView):
    """所有spu查询"""
    queryset = SPU.objects.all()
    serializer_class = SPUListSerializer


class SUPSpecView(ListAPIView):
    """spu规格信息查询"""

    def get_queryset(self):
        pk = self.kwargs['pk']
        return SPUSpecification.objects.filter(spu_id=pk)
    serializer_class = SPUSpecSerializer


