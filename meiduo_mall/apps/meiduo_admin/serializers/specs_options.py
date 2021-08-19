from rest_framework import serializers

from apps.goods.models import SpecificationOption, SPUSpecification


class SPUSpecOptionSerializer(serializers.ModelSerializer):
    """规格选项"""
    spec = serializers.StringRelatedField()
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        fields = '__all__'


class SpecSerializer(serializers.ModelSerializer):
    """规格"""
    class Meta:
        model = SPUSpecification
        fields = ['id', 'name']
