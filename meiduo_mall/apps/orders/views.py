from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""
    def get(self, request):
        user = request.user
        # 地址信息
        addresses = user.addresses.filter(is_deleted=False)
        address_list = []
        for address in addresses:
            address_list.append({
                'id': address.id,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'receiver': address.receiver,
                'mobile': address.mobile
            })
        # 购物车中的信息
        redis_conn = get_redis_connection('carts')
        pl = redis_conn.pipeline()
        pl.hgetall('cart_%s' % user.id)
        pl.smembers('selected_%s' % user.id)
        # result = [hash结果, set结果]
        result = pl.execute()
        sku_id_counts = result[0]
        selected_ids = result[1]
        # 转换二进制字典数据为普通字典
        selected_carts = {}
        for sku_id in selected_ids:
            selected_carts[int(sku_id)] = int(sku_id_counts[sku_id])
        skus = SKU.objects.filter(id__in=selected_carts.keys())
        sku_list = []
        for sku in skus:
            sku_list.append({
                'id': sku_id,
                'name': sku.name,
                'count': selected_carts[sku_id],
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })
        context ={
            'skus': sku_list,
            'address': address_list
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'context': context})


