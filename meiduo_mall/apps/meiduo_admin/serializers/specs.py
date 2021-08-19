from rest_framework import serializers

from apps.goods.models import SPUSpecification


class SPUSpecSerializer(serializers.ModelSerializer):
    """SPUspec数据"""
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = '__all__'

