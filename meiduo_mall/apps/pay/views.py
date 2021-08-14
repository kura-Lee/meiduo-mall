from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from alipay import AliPay, AliPayConfig
from django.views import View
from django.conf import settings
from apps.orders.models import OrderInfo
from apps.pay.models import Payment
from utils.views import LoginRequiredJSONMixin


class PaymentView(LoginRequiredJSONMixin, View):
    """订单支付功能"""

    def get(self, request, order_id):
        # 订单校验
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'],
                                          user=user)
        except OrderInfo.DoesNotExist:
            return JsonResponse({'code': 400, 'errmsg': '没有此订单'}, status=400)
        # 创建支付宝实例
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调 url
            app_private_key_string=settings.APP_PRIVATE_KEY_STRING,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=settings.ALIPAY_PUBLIC_KEY_STRING,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG,  # 默认 False
            verbose=False,  # 输出调试数据
            config=AliPayConfig(timeout=15)  # 可选，请求超时时间
        )
        # 调用支付方法
        # 电脑网站支付，需要跳转到：https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject=settings.ORDER_SUBJECT,
            return_url=settings.ALIPAY_RETURN_URL,
            notify_url="https://example.com/notify"   # 可选，不填则使用默认 notify url
        )
        # 拼接链接
        pay_url = settings.ALIPAY_URL + order_string
        # 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'alipay_url': pay_url})


class PaymentStatusView(View):
    """保存订单支付结果"""

    def get(self, request):
        # 获取前端传入的请求参数
        query_dict = request.GET
        data = query_dict.dict()
        # 获取并从请求参数中剔除signature
        signature = data.pop('sign')
        # 创建支付宝实例
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调 url
            app_private_key_string=settings.APP_PRIVATE_KEY_STRING,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=settings.ALIPAY_PUBLIC_KEY_STRING,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG,  # 默认 False
            verbose=False,  # 输出调试数据
            config=AliPayConfig(timeout=15)  # 可选，请求超时时间
        )
        # 调用验证支付方法
        success = alipay.verify(data, signature)
        if success:
            # 读取order_id
            order_id = data.get('out_trade_no')
            # 读取支付宝流水号
            trade_id = data.get('trade_no')
            # 保存Payment模型类数据
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            # 修改订单状态为待评价
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM["UNCOMMENT"])
            # 响应trade_id
            return JsonResponse({'code': 0, 'errmsg': 'OK', 'trade_id': trade_id})
        else:
            # 订单支付失败，重定向到我的订单
            return JsonResponse({'code': 400, 'errmsg': '非法请求'})