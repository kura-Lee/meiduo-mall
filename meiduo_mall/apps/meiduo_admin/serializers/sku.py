from rest_framework import serializers

from apps.goods.models import SKU, GoodsCategory, SPU, SpecificationOption, SPUSpecification, SKUSpecification
from django.db import transaction

class SKUSpecSerializre(serializers.ModelSerializer):
    """SKU规格"""
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification
        fields = ['spec_id', 'option_id']


class SKUSerializer(serializers.ModelSerializer):
    """SKU商品"""
    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    spu = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    # 添加商品的具体规格，实现保存
    specs = SKUSpecSerializre(many=True)

    class Meta:
        model = SKU
        fields = '__all__'

    def create(self, validated_data):
        # 获取规格信息,并从validated_data数据中,删除规格信息数据
        specs_data = validated_data.pop('specs')
        # 使用事务保证数据的原子性一致性
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                # 保存sku
                sku = SKU.objects.create(**validated_data)
                # 对规格信息进行遍历,来保存商品规格信息
                for spec_data in specs_data:
                    SKUSpecification.objects.create(sku=sku, **spec_data)
            except Exception:
                transaction.savepoint_rollback(save_point)
            else:
                transaction.savepoint_commit(save_point)
        # 返回sku
        return sku

    def update(self, instance, validated_data):
        specs_data = validated_data.pop('specs')
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                super().update(instance, validated_data)
                for spec in specs_data:
                    SKUSpecification.objects.filter(sku=instance, spec_id=spec.get('spec_id')).update(option_id=spec.get('option_id'))
            except Exception:
                transaction.savepoint_rollback(save_point)
            else:
                transaction.savepoint_commit(save_point)
        return instance

class GoodsCategorySerializer(serializers.ModelSerializer):
    """商品分类数据"""
    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']


class SPUListSerializer(serializers.ModelSerializer):
    """SPU数据"""
    class Meta:
        model = SPU
        fields = ['id', 'name']


class SPUSpecOptionSerializer(serializers.ModelSerializer):
    """SPU规格选项"""
    class Meta:
        model = SpecificationOption
        fields = ['id', 'value']


class SPUSpecSerializer(serializers.ModelSerializer):
    """SPU规格"""
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()
    # 关联序列化返回 规格选项信息
    options = SPUSpecOptionSerializer(many=True)  # 使用规格选项序列化器

    class Meta:
        model = SPUSpecification
        fields = '__all__'








