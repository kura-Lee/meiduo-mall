from rest_framework import serializers

from apps.goods.models import SKUImage, SKU


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKUImage
        fields = "__all__"

    def update(self, instance, validated_data):
        image_data = validated_data.get('image').read()
        from fdfs_client.client import Fdfs_client
        cilent = Fdfs_client('utils/FastDFS/client.conf')
        result = cilent.upload_by_buffer(image_data)
        if result['Status'] != 'Upload successed.':
            raise serializers.ValidationError('上传失败')
        file_id = result['Remote file_id']
        instance.sku_id = validated_data.get('sku')
        instance.image = file_id
        instance.save()
        return instance


class ImageSKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ['id', "name"]
