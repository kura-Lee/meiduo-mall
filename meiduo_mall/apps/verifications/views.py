from random import randint

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django_redis import get_redis_connection
from libs.captcha.captcha import captcha
from django.views import View
from libs.yuntongxun.sms import send_sms
import logging
logger = logging.getLogger('django')

class ImageCodeView(View):
    """产生图形验证码"""
    def get(self, request, uuid):
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection('code')
        # 5mins有效
        redis_conn.setex('img_%s' % uuid, 300, text)
        # print(text)
        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):
    """产生短信验证码"""
    def get(self, request, mobile):
        image_code = request.GET.get('image_code')
        if image_code == '':
            return JsonResponse({'code': 400, 'errmsg': '请填写图片验证码！'})
        # 查询图片验证码
        image_code_id = request.GET.get('image_code_id')
        redis_conn = get_redis_connection('code')
        text = redis_conn.get('img_%s' % image_code_id)
        if text is None:
            return JsonResponse({'code': 400, 'errmsg': '图片验证码过期或不存在！'})
        else:
            # 转换为str
            text = text.decode()
            # 有这个图片验证码将其从数据库删除
            try:
                redis_conn.delete('img_%s' % image_code_id)
            except Exception as e:
                logger.error(e)
        # 频繁验证校验
        if redis_conn.get('send_flag_%s' % mobile):
            return JsonResponse({'code': 401, 'errmsg': '请求过于频繁，请稍后再试！'})
        # 图片验证码校验
        if image_code.lower() == text.lower():
            # print("校验成功")
            sms_code = '%06d' % randint(0, 999999)
            print(sms_code)
            # 设置频繁请求短信验证码falg
            redis_conn.setex('send_flag_%s' % mobile, 60, 1)
            # res = send_sms(mobile, [sms_code, 5], 1)
            from celery_tasks.sms.tasks import send_sms_code
            res = send_sms_code.delay(mobile, sms_code)
            if res == -1:
                print("发送失败")
                return JsonResponse({'code': 0, 'errmsg': '短信发送失败'})
            else:
                print("发送成功")
                redis_conn.setex('sms_%s' % mobile, 300, sms_code)
                return JsonResponse({'code': 0, 'errmsg': '短信发送成功'})
        else:
            # print("校验失败")
            return JsonResponse({'code': 400, 'errmsg': '图片验证码错误'})