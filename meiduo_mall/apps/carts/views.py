import base64
import json
import pickle

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from apps.goods.models import SKU


class CartView(View):
    """购物车"""
    def post(self, request):
        """添加购物车"""
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        # 选中状态未传默认为true
        selected = data.get('select')
        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'errmsg': "参数不全"}, status=400)
        try:
            sku = SKU.objects.get(id=sku_id)
        except sku.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': "没有此商品"}, status=400)
        try:
            count = int(count)
        except:
            return JsonResponse({'code': 400, 'errmsg': "参数错误"}, status=400)
        if selected:
            if not isinstance(selected, bool):
                return JsonResponse({'code': 400, 'errmsg': "参数错误"}, status=400)
        else:
            selected = False
        # 根据用户的登录状态保存数据
        user = request.user
        if user.is_authenticated:
            # 用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # cart_%s  sku_id1 count1 sku_id2 count2 。。。
            # hincrby(self, name, key, amount=1)
            # 将key为name的 filed为key的 的value 增加amount
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            pl.execute()
            return JsonResponse({'code': 400, 'errmsg': 'ok'})
        else:
            # 用户未登录，操作cookie购物车
            cart_str = request.COOKIES.get('carts')
            # 如果用户操作过cookie购物车
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
                print(cart_dict)
            else:
                # 用户从没有操作过cookie购物车
                cart_dict = {}
            # 判断要加入购物车的商品是否已经在购物车中,如有相同商品，累加求和，反之，直接赋值
            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            print(cart_dict)
            # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # 创建响应对象
            response = JsonResponse({'code': 0, 'errmsg': '添加购物车成功'})
            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('carts', cookie_cart_str, max_age=7 * 24 * 3600)
            return response

    def get(self, request):
        """获取购物车信息"""
        user = request.user
        # 登录用户从redis获取数据
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            redis_cart_dict = redis_conn.hgetall('cart_%s' % user.id)
            selected_list = redis_conn.smembers('selected_%s' % user.id)
            # 将redis中的数据构造成跟cookie中的格式一致，方便统一查询
            cart_dict = {}
            for sku_id, count in redis_cart_dict.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in selected_list
                }
        # 未登录用户从cookie获取数据
        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        # 组合数据
        sku_ids = cart_dict.keys()
        try:
            skus = SKU.objects.filter(id__in=sku_ids)
        except Exception:
            return JsonResponse({'code': 400, 'errmsg': "参数错误"}, status=400)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                "id": sku.id,
                "name": sku.name,
                "count": cart_dict.get(sku.id).get('count'),
                "selected": cart_dict.get(sku.id).get('selected'),
                "default_image_url": sku.default_image.url,
                "price": str(sku.price),
                "amount": str(sku.price * cart_dict.get(sku.id).get('count')),
            })
        return JsonResponse({'code': 0, 'errmsg': 'ok', "cart_skus": cart_skus})

    def put(self, request):
        """在购物车页面修改数据"""
        data = json.loads(request.body.decode())
        sku_id = data.get('sku_id')
        count = data.get('count')
        selected = data.get('selected')
        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'errmsg': "参数不全"}, status=400)
        try:
            sku = SKU.objects.get(id=sku_id)
        except sku.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': "没有此商品"}, status=400)
        try:
            count = int(count)
        except:
            return JsonResponse({'code': 400, 'errmsg': "参数错误"}, status=400)
        if selected:
            if not isinstance(selected, bool):
                return JsonResponse({'code': 400, 'errmsg': "参数错误"}, status=400)
        else:
            selected = False

        #根据用户是否登录做出不同的查询修改
        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hset('cart_%s' % user.id, sku_id, count)
            #是否选中
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count
            }
            return JsonResponse({'code': 0, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
        else:
            # 未登录用户，使用cookie进行设置
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}
            # 因为接口设计为幂等的，直接覆盖
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            #响应对象
            cart_sku = {
                'id': sku_id,
                'name': sku.name,
                'count': count,
                'selected': selected,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count
            }
            response = JsonResponse({'code': 0, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
            response.set_cookie('carts', cookie_cart_str, max_age=3600*24*7)
            return response

    def delete(self, request):
        """购物车删除"""
        sku_dict = json.loads(request.body.decode())
        sku_id = sku_dict.get('sku_id')
        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception as e:
            print(e)
            return JsonResponse({'coed': 400, 'errmsg': '参数错误'}, status=400)
        user = request.user
        if user.is_authenticated:
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hdel('cart_%s' % user.id, sku_id)
            pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        else:
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                return JsonResponse({'coed': 400, 'errmsg': '参数错误'}, status=400)
            if sku_id in cart_dict:
                del cart_dict[sku_id]

            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('carts', cookie_cart_str, max_age=3600*24*7)
        return response

class CartsSelectAllView(View):
    """全选购物车"""
    def put(self, request):
        select_dict = json.loads(request.body.decode())
        select_all = select_dict.get('selected')
        if not isinstance(select_all, bool):
            return JsonResponse({'coed': 400, 'errmsg': '参数错误'}, status=400)
        user = request.user
        if user.is_authenticated:
            # 用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            sku_id_list = redis_conn.hkeys('cart_%s' % user.id)
            if select_all:
                # 全选
                redis_conn.sadd('selected_%s' % user.id, *sku_id_list)
            else:
                # 取消全选
                redis_conn.srem('selected_%s' % user.id, *sku_id_list)
            return JsonResponse({'code': 0, 'errmsg': '全选购物车成功'})
        else:
            # 用户未登录，操作cookie购物车
            cart_str = request.COOKIES.get('carts')
            response = JsonResponse({'code': 0, 'errmsg': '全选购物车成功'})
            if cart_str is not None:
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
                for sku_id in cart_dict:
                    cart_dict[sku_id]['selected'] = select_all
                cookie_cart = base64.b64encode(pickle.dumps(cart_dict)).decode()
                response.set_cookie('carts', cookie_cart, max_age=7 * 24 * 3600)
            else:
                return JsonResponse({'coed': 400, 'errmsg': '参数错误'}, status=400)
            return response


class CartsSimpleView(View):
    """商品页面右上角购物车的展示"""

    def get(self, request):
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，查询Redis购物车
            redis_conn = get_redis_connection('carts')
            redis_cart_dict = redis_conn.hgetall('cart_%s' % user.id)
            selected_list = redis_conn.smembers('selected_%s' % user.id)
            # 将redis中的数据构造成跟cookie中的格式一致，方便统一查询
            cart_dict = {}
            for sku_id, count in redis_cart_dict.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in selected_list
                }
        else:
            # 用户未登录，查询cookie购物车
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes,再将bytes转成base64的bytes,最后将bytes转字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        # 组合数据
        sku_ids = cart_dict.keys()
        try:
            skus = SKU.objects.filter(id__in=sku_ids)
        except Exception:
            return JsonResponse({'code': 400, 'errmsg': "参数错误"}, status=400)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                "id": sku.id,
                "name": sku.name,
                "count": cart_dict.get(sku.id).get('count'),
                "default_image_url": sku.default_image.url,
            })
        return JsonResponse({'code': 0, 'errmsg': 'ok', "cart_skus": cart_skus})