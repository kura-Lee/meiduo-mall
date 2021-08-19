from rest_framework import serializers

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods


class OrderInfoSerializer(serializers.ModelSerializer):
    """订单列表"""
    class Meta:
        model = OrderInfo
        fields = ['order_id', 'create_time']


class OrderSKUSerializer(serializers.ModelSerializer):
    """订单商品需要的sku的部分信息"""
    class Meta:
        model = SKU
        fields = ['name', 'default_image']


class OrderGoodsSerializer(serializers.ModelSerializer):
    """订单商品信息"""
    sku = OrderSKUSerializer()
    class Meta:
        model = OrderGoods
        fields = ['count', 'price', 'sku']

class OrderDetailSerializer(serializers.ModelSerializer):
    """订单详细信息"""
    skus = OrderGoodsSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = ['order_id', 'user', 'total_count', 'total_amount', 'freight', 'pay_method', 'status', 'create_time', 'skus']




