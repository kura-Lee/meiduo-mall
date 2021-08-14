from django.test import TestCase

# Create your tests here.


from alipay import AliPay, AliPayConfig
from meiduo_mall import settings

alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调 url
            app_private_key_string=settings.APP_PRIVATE_KEY_STRING,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=settings.ALIPAY_PUBLIC_KEY_STRING,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=False,  # 默认 False
            verbose=False,  # 输出调试数据
            config=AliPayConfig(timeout=15)  # 可选，请求超时时间
        )
# 调用支付方法
# 电脑网站支付，需要跳转到：https://openapi.alipay.com/gateway.do? + order_string
order_strig = alipay.api_alipay_trade_page_pay(
    out_trade_no='1234344',
    total_amount='98',
    subject=settings.ORDER_SUBJECT,
    return_url=settings.ALIPAY_RETURN_URL,
    notify_url="https://example.com/notify"   # 可选，不填则使用默认 notify url
)
# 拼接链接
pay_url = settings.ALIPAY_URL + order_strig

print(pay_url)