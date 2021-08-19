from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SpecificationOption, SPUSpecification
from apps.meiduo_admin.serializers.specs_options import SPUSpecOptionSerializer, SpecSerializer
from apps.meiduo_admin.utils import PageNum


class Spec_optionAPIViewSet(ModelViewSet):
    """规格的选项options"""
    queryset = SpecificationOption.objects.all()
    serializer_class = SPUSpecOptionSerializer
    pagination_class = PageNum


class SpecListAPIView(ListAPIView):
    """规格查询"""
    queryset = SPUSpecification.objects.all()
    serializer_class = SpecSerializer

# class Spec_Option_RetrieveAPIView(RetrieveAPIView):
#     """获取具体的规格选项"""
#     queryset = SpecificationOption.objects.all()
#     serializer_class = SPUSpecOptionSerializer

