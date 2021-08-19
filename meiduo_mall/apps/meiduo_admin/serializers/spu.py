from rest_framework import serializers

from apps.goods.models import SPU, Brand


class SPUSerializer(serializers.ModelSerializer):
    """SPU"""
    brand = serializers.StringRelatedField()
    brand_id = serializers.IntegerField()
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()

    class Meta:
        model = SPU
        fields = ['id', 'name', 'brand', 'brand_id', 'category1_id',\
                  'category2_id', 'category3_id', "sales", "comments",\
                  "desc_detail", "desc_pack", "desc_service"]
        extra_kwargs = {
            'id': {'required': False},
        }



class BrandSerializer(serializers.ModelSerializer):
    """Brand"""
    class Meta:
        model = Brand
        fields = ['id', 'name']



