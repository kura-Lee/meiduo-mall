from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SPU, Brand, GoodsCategory
from apps.meiduo_admin.serializers.sku import GoodsCategorySerializer
from apps.meiduo_admin.serializers.spu import SPUSerializer, BrandSerializer
from apps.meiduo_admin.utils import PageNum


class SPUAPIViewSet(ModelViewSet):
    """商品SPU"""
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            queryset = SPU.objects.filter(name__contains=keyword)
        else:
            queryset = SPU.objects.all()
        return queryset
    serializer_class = SPUSerializer
    pagination_class = PageNum


class BrandAPIView(ListAPIView):
    """商品品牌信息"""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class CategoryOneAPIView(ListAPIView):
    """获取一级分类信息"""
    queryset = GoodsCategory.objects.filter(parent=None)
    serializer_class = GoodsCategorySerializer


class CategoryOtherAPIView(ListAPIView):
    """获取二三级分类信息"""
    def get_queryset(self):
        parent = self.kwargs.get('pk')
        return GoodsCategory.objects.filter(parent=parent)
    serializer_class = GoodsCategorySerializer

