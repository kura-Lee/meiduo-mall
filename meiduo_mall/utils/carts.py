import base64
import pickle
from django_redis import get_redis_connection

def merge_cart_cookie_to_redis(request, user, response):
    """
    获取客户cookie数据，合并到数据库
    :param request: 本次请求对象，获取cookie中的数据
    :param user: 登录用户信息，获取user_id
    :param response: 本次响应对象，清除cookie中的数据
    :return: response
    """
    # 获取cookie中的购物车数据
    cookie_cart_str = request.COOKIES.get('carts')
    # cookie中没有数据就直接响应结果
    if not cookie_cart_str:
        return response
    cookie_cart_dict = pickle.loads(base64.b64decode(cookie_cart_str.encode()))
    # 将cookie数据转换为跟redis中数据结构类似的
    new_cart_dict = {}
    # cookie中选中的sku_id列表, 需要添加
    new_select_add_list = []
    # cookie中未选中的sku_id列表,需要移除
    new_select_rem_list = []
    for sku_id, data_dict in cookie_cart_dict.items():
        new_cart_dict[sku_id] = data_dict['count']
        if data_dict["selected"]:
            new_select_add_list.append(sku_id)
        else:
            new_select_rem_list.append(sku_id)
    # 将new_cart_dict合并到Redis数据库
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    pl.hmset('cart_%s' % user.id, new_cart_dict)
    # 将勾选状态同步到Redis数据库
    if new_select_add_list:
        pl.sadd('selected_%s' % user.id, *new_select_add_list)
    if new_select_rem_list:
        pl.srem('selected_%s' % user.id, *new_select_rem_list)
    pl.execute()
    # 清除cookie
    response.delete_cookie('carts')

    return response




