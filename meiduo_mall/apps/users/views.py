import json

from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.users.models import User
import re
from apps.users.form import RegisterForm
from django_redis import get_redis_connection
import logging
logger = logging.getLogger("django")

class UsernameCountView(View):
    """
    用户名重复的验证
    """
    def get(self, request, username):
        # if not re.match('[a-zA-Z0-9_-]{5,20}', username):
        #     return JsonResponse({'code': 200, 'errormsg': '用户名不满足规则'})
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'count': count, 'errormsg': 'ok'})

class MobileCountView(View):
    """
    手机号的重复验证
    """
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        print("手机号码重复：",count)
        return JsonResponse({'code': 0, 'count': count, 'errormsg': 'OK'})


class UserRegisterView(View):
    """
    用户注册
    """
    def post(self, request):
        # form = RegisterForm(request.POST, request=request)
        # if form.is_valid():
        #     username = form.cleaned_data.get('username')
        #     password = form.cleaned_data.get('password')
        #     mobile = form.cleaned_data.get('mobile')
        #     # form.cleaned_data.get('sms_code')
        #     print(username, password, mobile)
        #     print(11111)
        # print(form.errors)
        # print(2222222222222)

        json_str = request.body.decode()
        parameter_dict = json.loads(json_str)
        print(parameter_dict)
        username = parameter_dict.get('username')
        password = parameter_dict.get('password')
        password2 = parameter_dict.get('password2')
        mobile = parameter_dict.get('mobile')
        sms_code = parameter_dict.get('sms_code')
        allow = bool(parameter_dict.get('allow'))
        if not all([username, password, password2, mobile, sms_code, allow]):
            return JsonResponse({'code':400, 'errmsg':'缺少必传参数!'})
        if allow != True:
            return JsonResponse({'code': 400, 'errmsg': '请勾选用户协议'})
        redis_conn = get_redis_connection('code')
        sms = redis_conn.get('sms_%s' % mobile)
        if sms is None:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码已过期'})
        else:
            sms = sms.decode()
            try:
                redis_conn.delete('sms_%s' % mobile)
            except Exception as e:
                logger.error(e)
        if sms_code != sms:
            return JsonResponse({'code': 400, 'errmsg': '请输入正确的验证码'})
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return JsonResponse({'code': 400, 'errmsg': '用户名在5到20位，且只能包含大小写字母数字和下划线'})
        if not re.match(r'^[0-9a-zA-Z!@#$%^&*]{8,20}$', password):
            return JsonResponse({'code': 400, 'errmsg': '密码在8到20位，且只能包含大小写字母数字和特殊字符'})
        if password != password2:
            return JsonResponse({'code': 400, 'errmsg': '两次密码输入不一致'})
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400, 'errmsg': '请输入正确的手机号'})
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
            print("创建用户")
        except Exception as e:
            # print(e)
            return JsonResponse({'code': 400, 'errmsg': '注册失败'})
        login(request, user)
        return JsonResponse({'code': 0, 'errmsg': '注册成功'})
