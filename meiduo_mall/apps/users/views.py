import json
from datetime import timedelta
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.users.models import User
import re
from apps.users.form import RegisterForm
from django_redis import get_redis_connection
import logging
logger = logging.getLogger("django")
from utils.views import LoginRequiredJSONMixin



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
        return JsonResponse({'code': 0, 'count': count, 'errormsg': 'OK'})


class UserRegisterView(View):
    """
    用户注册
    """
    def post(self, request):
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
        # 短信验证码校验
        redis_conn = get_redis_connection('code')
        sms = redis_conn.get('sms_%s' % mobile)
        if sms is None:
            return JsonResponse({'code': 400, 'errmsg': '短信验证码不存在或已过期'})
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
        response = JsonResponse({'code': 0, 'errmsg': '注册成功'})
        response.set_cookie('username', user.username)
        request.session.set_expiry(0)
        return response


class LoginView(View):
    def post(self, request):
        data = json.loads(request.body.decode())
        username = data.get("username")
        password = data.get("password")
        remembered = data.get("remembered")
        if not all([username, password]):
            return JsonResponse({'code': '400', 'errmsg': '请输入用户名或密码'})
        # 手机号登录
        if re.match(r'^1[3-9]\d{9}$', username):
            # 修改django认证字段为mobile
            User.USERNAME_FIELD = 'mobile'
        else:
            User.USERNAME_FIELD = 'username'
        user = authenticate(username=username, password=password)
        if not user:
            return JsonResponse({'code': '400', 'errmsg': '用户名或密码错误'})
        login(request, user)
        if remembered:
            request.session.set_expiry(timedelta(days=10))
        else:
            request.session.set_expiry(0)
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', user.username, max_age=3600 * 24 * 10)
        return response


class LogoutView(View):
    def delete(self, request):
        logout(request)
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')
        return response


class UserInfoView(LoginRequiredJSONMixin, View):
    def get(self, request):
        """个人信息界面"""
        return JsonResponse({
            'code': 0,
            'errmsg': '个人中心',
            "info_data": {
                "username": request.user.username,
                "mobile": request.user.mobile,
                "email": request.user.email,
                "email_active": request.user.email_active
            }
        })

    def put(self, request):
        pass

