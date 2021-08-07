import json
import re

from django import http
from django.conf import settings
from django.contrib.auth import login
from django.db import DatabaseError
from django.http import HttpResponseBadRequest, JsonResponse
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
import logging

from django_redis import get_redis_connection

from apps.oauth.utils import QQ_access_token
from apps.users.models import OAuthQQUser, User

logger = logging.getLogger('django')

class QQAuthURLView(View):
    """提供QQ登录页面网址
    https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=xxx&redirect_uri=xxx&state=xxx
    """
    def get(self, request):
        # next表示从哪个页面进入到的登录页面，将来登录成功后，就自动回到那个页面
        next = request.GET.get('next')

        # 获取QQ登录页面网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=next)
        login_url = oauth.get_qq_url()
        return http.JsonResponse({'code': 0, 'errmsg': 'OK', 'login_url': login_url})


class QQAuthUserView(View):
    """
    扫码登录的回调处理
    """
    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return HttpResponseBadRequest('缺少code')
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': 'oauth2.0认证失败'})
        try:
            oauth_qq = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 未绑定用户
            access_token = QQ_access_token.generate_access_token({'openid': openid})
            return http.JsonResponse({'code': 300, 'errmsg': 'ok', 'access_token': access_token})
        else:
            # 绑定用户
            user = oauth_qq.user
            login(request, user)
            response = JsonResponse({'code': 0, 'errmsg': 'ok'})
            response.set_cookie('username', user.username, max_age=3600*24*10)
            return response

    def post(self, request):
        """绑定用户到openid"""
        data_dict = json.loads(request.body.decode())
        mobile = data_dict.get('mobile')
        password = data_dict.get('password')
        sms_code_client = data_dict.get('sms_code')
        access_token = data_dict.get('access_token')
        print("获取到查询数据")
        if not all([mobile, password, sms_code_client]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400, 'errmsg': '请输入正确的手机号码'})
        if not re.match(r'^[0-9a-zA-Z!@#$%^&*]{8,20}$', password):
            return JsonResponse({'code': 400, 'errmsg': '密码在8到20位，且只能包含大小写字母数字和特殊字符'})
        redis_conn = get_redis_connection('code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        if sms_code_server is None:
            return JsonResponse({'code': 401, 'errmsg': '验证码失效'})
        if sms_code_server.decode() != sms_code_client:
            return JsonResponse({'code': 401, 'errmsg': '验证码错误'})
        openid = QQ_access_token.check_access_token(access_token)
        if not openid:
            return JsonResponse({'code': 400, 'errmsg': '缺少openid'})
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        else:
            if not user.check_password(password):
                return JsonResponse({'code': 400, 'errmsg': '输入的密码不正确'})
        try:
            OAuthQQUser.objects.create(openid=openid, user=user)
        except DatabaseError:
            return JsonResponse({'code': 400, 'errmsg': '向数据库添加数据失败'})
        login(request, user)
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', user.username, max_age=3600*24*10)
        return response


