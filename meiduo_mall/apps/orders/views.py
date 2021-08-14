import json
from logging import getLogger
from time import sleep

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
from utils.views import LoginRequiredJSONMixin

logger = getLogger('django')


class OrderSettlementView(View):
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
                'id': sku.id,
                'name': sku.name,
                'count': selected_carts[sku.id],
                'default_image_url': sku.default_image.url,
                'price': sku.price
            })
        # 补充运费
        from decimal import Decimal
        freight = Decimal('10.00')
        context ={
            'skus': sku_list,
            'addresses': address_list,
            'freight': freight,
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'context': context})


class OrderCommitView(LoginRequiredJSONMixin, View):
    """订单提交"""

    def post(self, request):
        """保存订单信息和订单商品信息"""
        data = json.loads(request.body.decode())
        address_id = data.get('address_id')
        pay_method = data.get('pay_method')
        if not all([address_id, pay_method]):
            return JsonResponse({'code': 400, 'errmsg': '请选择地址信息和支付方式', 'order_id': None})
        # 判断address_id是否合法
        try:
            address = Address.objects.get(id=address_id)
        except Exception:
            return JsonResponse({'code': 400, 'errmsg': '参数address_id错误', 'order_id': None}, status=400)
        # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return JsonResponse({'code': 400, 'errmsg': '参数pay_method错误', 'order_id': None}, status=400)

        user = request.user
        # 保存订单基本信息 OrderInfo（一）
        # 生成订单编号：年月日时分秒+用户编号
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        # 支付方式生成订单状态
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']
        # 总数量，总金额
        total_count = 0
        from decimal import Decimal
        total_amount = Decimal('0')
        # 运费
        freight = Decimal('10.00')
        # 开启事务
        with transaction.atomic():
            # 创建事务保存点
            save_id = transaction.savepoint()
            try:
                # 暂时保存订单信息中的count和amount为0，等下面订单商品循环遍历再计算
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=total_count,
                    total_amount=total_amount,
                    freight=freight,
                    pay_method=pay_method,
                    status=status,
                )
                # 从redis读取购物车中被勾选的商品信息
                redis_conn = get_redis_connection('carts')
                redis_cart = redis_conn.hgetall('cart_%s' % user.id)
                selected = redis_conn.smembers('selected_%s' % user.id)
                carts = {}
                for sku_id in selected:
                    carts[int(sku_id)] = int(redis_cart[sku_id])
                sku_ids = carts.keys()
                skus = SKU.objects.filter(id__in=sku_ids)
                for sku in skus:
                    for _ in range(10):
                        # 读取原始库存
                        origin_stock = sku.stock
                        origin_sales = sku.sales
                        # 判断库存是否足够
                        sku_count = carts[sku.id]
                        if sku_count > sku.stock:
                            # 库存不足，回滚，返回响应
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'code': 400, 'errmsg': '库存不足'})
                        # 减少库存，增加销量
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()
                        # 乐观锁更新库存和销量
                        new_stock = origin_stock - sku_count
                        new_sales = origin_sales + sku_count
                        result = SKU.objects.filter(id=sku.id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                        # 如果(由于库存改变导致的)下单失败，但是库存足够时，继续下单，直到下单成功或者库存不足为止
                        if result == 0:
                            sleep(0.005)
                            continue
                        # 保存订单商品信息 OrderGoods（多）
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price,
                        )
                        # 保存商品订单中总价和总数量
                        order.total_count += sku_count
                        order.total_amount += (sku_count * sku.price)
                        # 下单成功或出问题，跳出循环
                        break
                # 添加邮费和保存订单信息
                order.total_amount += order.freight
                order.save()
            except Exception as e:
                # 出错记录日志并回滚
                logger.error(e)
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'code': 400, 'errmsg': '下单失败'})
            # 提交订单成功，显式的提交一次事务
            transaction.savepoint_commit(save_id)

        # 删除购物车中已结算(勾选)的信息
        pl = redis_conn.pipeline()
        if selected:
            pl.hdel('cart_%s' % user.id, *selected)
            pl.srem('selected_%s' % user.id, *selected)
        pl.execute()
        # 响应提交订单结果
        return JsonResponse({'code': 0, 'errmsg': '下单成功', 'order_id': order_id})


