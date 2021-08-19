from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SKUImage, SKU
from apps.meiduo_admin.serializers.image import ImageSerializer, ImageSKUSerializer
from apps.meiduo_admin.utils import PageNum
from fdfs_client.client import Fdfs_client

class ImageAPIViewSet(ModelViewSet):
    """图片的增删改查"""
    queryset = SKUImage.objects.all()
    serializer_class = ImageSerializer
    pagination_class = PageNum

    def create(self, request, *args, **kwargs):
        """dfs上传图片，并入库(新增)"""
        image = request.FILE.get('image')
        sku_id = request.data.get('sku')
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        client = Fdfs_client('utils/FastDFS/client.conf')
        result = client.upload_by_buffer(image.read())
        if result['Status'] != 'Upload successed.':
            return Response(status=status.HTTP_403_FORBIDDEN)
        file_id = result['Remote file_id']
        new_image = SKUImage.objects.create(sku_id=sku_id, image=file_id)
        return Response({'id': new_image.id,
                         'sku': sku_id,
                         'image': new_image.image.url
                         }, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        """重写删除，使其一并删除fastdfs的数据"""
        remoteid = instance.image
        client = Fdfs_client('utils/FastDFS/client.conf')
        result = client.delete_file(remoteid)
        if result[0] != 'Delete file successed.':
            return Response(status=status.HTTP_403_FORBIDDEN)
        instance.delete()


class ImageSKUAPIView(ListAPIView):
    """新增图片的sku查询"""
    queryset = SKU.objects.all()
    serializer_class = ImageSKUSerializer