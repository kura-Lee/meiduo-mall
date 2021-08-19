from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.serializers.order import OrderInfoSerializer, OrderDetailSerializer
from apps.meiduo_admin.utils import PageNum
from apps.orders.models import OrderInfo


class OrderInfoAPIView(ListAPIView):
    """查询订单信息"""
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return OrderInfo.objects.filter(order_id=keyword)
        return OrderInfo.objects.all()

    serializer_class = OrderInfoSerializer
    pagination_class = PageNum


class OrderDetailAPIView(RetrieveAPIView):
    """订单详情"""
    queryset = OrderInfo.objects.all()
    serializer_class = OrderDetailSerializer



class OrderStatusAPIView(APIView):
    """更新订单状态"""
    def put(self, request, order_id):
        order_status = request.data.get('status')
        try:
            order = OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if order_status not in OrderInfo.ORDER_STATUS_ENUM.values():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        order.status = order_status
        order.save()
        return Response({'order_id': order.order_id, 'status': order.status})



