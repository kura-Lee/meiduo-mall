import json
from datetime import timedelta
from django.contrib.auth import login, authenticate, logout
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.areas.models import Area
from apps.users.models import User, Address, USER_ADDRESS_COUNTS_LIMIT
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


class UserEmailView(LoginRequiredJSONMixin, View):

    def put(self, request):
        json_dict = json.loads(request.body.decode())
        email = json_dict.get('email')
        if not re.match(r'^[a-z0-9][\w\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return JsonResponse({'code': 400, 'errmsg': '参数email有误'}, status=400)
        try:
            user = request.user
            user.email = email
            user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '添加邮箱失败'}, status=400)
        # 异步发送验证邮件
        from celery_tasks.email.tasks import send_email
        from apps.users.utils import generate_verify_email_url
        verify_url = generate_verify_email_url(user)
        send_email.delay(email, verify_url)
        return JsonResponse({'code': 0, 'errmsg': '添加邮箱成功'})

class VerifyEmailView(View):
    def put(self, request):
        token = request.GET.get('token')
        if not token:
            return JsonResponse({'code': 400, 'errmsg': 'token缺少'})
        from apps.users.utils import check_verify_email_url
        data_dict = check_verify_email_url(token)
        try:
            user = User.objects.get(pk=data_dict.get('user_id'), email=data_dict.get('email'))
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '参数有误!'})
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '数据库保存出错,激活失败!'})
        else:
            return JsonResponse({'code': 0, 'errmsg': '激活成功!'})


class ChangePasswordView(LoginRequiredJSONMixin, View):
    """修改密码"""
    def put(self, request):
        # 接收参数
        dict = json.loads(request.body.decode())
        old_password = dict.get('old_password')
        new_password = dict.get('new_password')
        new_password2 = dict.get('new_password2')

        # 校验参数
        if not all([old_password, new_password, new_password2]):
            return JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        result = request.user.check_password(old_password)
        if not result:
            return JsonResponse({'code': 400, 'errmsg': '原始密码不正确'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return JsonResponse({'code': 400, 'errmsg': '密码最少8位,最长20位'})
        if new_password != new_password2:
            return JsonResponse({'code': 400, 'errmsg': '两次输入密码不一致'})
        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '修改密码失败'})
        # 清理状态保持信息
        logout(request)
        response = JsonResponse({'code': 0, 'errmsg': '修改密码成功'})
        response.delete_cookie('username')
        # 响应密码修改结果：重定向到登录界面
        return response


class CreateAddressView(LoginRequiredJSONMixin, View):
    """新增用户地址"""
    def post(self, request):
        if request.user.addresses.count() > USER_ADDRESS_COUNTS_LIMIT:
            return JsonResponse({'code': 400, 'errmsg': '超过地址数量上限'})
        data = json.loads(request.body.decode())
        keys = ["receiver", "province_id", "city_id", "district_id", "place", "mobile"]
        for key in keys:
            if data.get(key) is None:
                return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        if not re.match(r'^1[3-9]\d{9}$', data['mobile']):
            return JsonResponse({'code': 400, 'errmsg': '手机格式错误'})
        if data.get('tel'):
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', data.get('tel')):
                return JsonResponse({'code': 400, 'errmsg': '固定电话格式错误'})
        if data.get('email'):
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', data.get('email')):
                return JsonResponse({'code': 400, 'errmsg': '邮箱格式错误'})
        try:
            address = Address.objects.create(
                user=request.user,
                title=data['receiver'],
                receiver=data['receiver'],
                province_id=data['province_id'],
                city_id=data['city_id'],
                district_id=data['district_id'],
                place=data['place'],
                mobile=data['mobile'],
                tel=data.get('tel'),
                email=data.get('email')
            )
            # 默认地址
            if not request.user.default_address:
                request.user.default_address = address
                request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '地址错误'})
        res = address.to_dict()
        res.pop('is_deleted')
        res['province'] = address.province.name
        res['city'] = address.city.name
        res['district'] = address.district.name
        return JsonResponse({'code': 0, 'errmsg': '新增地址成功', 'address': res})



class AddressView(LoginRequiredJSONMixin, View):
    # 查询地址
    def get(self, request):
        # 获取所有的地址:
        addresses = Address.objects.filter(user=request.user, is_deleted=False)
        address_dict_list = []
        for address in addresses:
            data = address.to_dict()
            data.pop('is_deleted')
            data['province'] = address.province.name
            data['city'] = address.city.name
            data['district'] = address.district.name
            # 默认地址放到最前面
            if request.user.default_address:
                if request.user.default_address.id == address.id:
                    address_dict_list.insert(0, data)
            else:
                address_dict_list.append(data)
        default_id = None
        if request.user.default_address:
            default_id = request.user.default_address.id
        return JsonResponse({'code': 0, 'errmsg': 'ok',
                             'addresses': address_dict_list,
                             'default_address_id': default_id})

    # 更新地址
    def put(self, request, address_id):
        data = json.loads(request.body.decode())
        keys = ["receiver", "province_id", "city_id", "district_id", "place", "mobile"]
        for key in keys:
            if data.get(key) is None:
                return JsonResponse({'code': 400, 'errmsg': '参数不全'})
        if not re.match(r'^1[3-9]\d{9}$', data['mobile']):
            return JsonResponse({'code': 400, 'errmsg': '手机格式错误'})
        if data.get('tel'):
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', data.get('tel')):
                return JsonResponse({'code': 400, 'errmsg': '固定电话格式错误'})
        if data.get('email'):
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', data.get('email')):
                return JsonResponse({'code': 400, 'errmsg': '邮箱格式错误'})
        try:
            Address.objects.filter(id=int(address_id)).update(
                user=request.user,
                title=data['receiver'],
                receiver=data['receiver'],
                province_id=data['province_id'],
                city_id=data['city_id'],
                district_id=data['district_id'],
                place=data['place'],
                mobile=data['mobile'],
                tel=data.get('tel'),
                email=data.get('email')
            )
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '更新错误'})
        address = Address.objects.get(id=address_id)
        res = address.to_dict()
        res.pop('is_deleted')
        res['province'] = address.province.name
        res['city'] = address.city.name
        res['district'] = address.district.name
        print(res)
        return JsonResponse({'code': 0, 'errmsg': '修改地址成功', 'address': res})
    # 删除地址
    def delete(self, request, address_id):
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)
            # 将地址逻辑删除设置为True
            address.is_deleted = True
            # 若删除默认地址，将user中的默认地址置空
            if int(address_id) == request.user.default_address.id:
                request.user.default_address = None
                request.user.save()
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '删除地址失败'}, status=400)
            # 响应删除地址结果
        return JsonResponse({'code': 0, 'errmsg': '删除地址成功'})


class DefaultAddress(LoginRequiredJSONMixin, View):
    """设置默认地址"""
    def put(self, request, address_id):
        try:
            address = Address.objects.get(id=address_id)
            request.user.default_address = address
            request.user.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '设置默认地址失败'}, status=400)
        return JsonResponse({'code': 0, 'errmsg': '设置默认地址成功'})


class TitleAddress(LoginRequiredJSONMixin, View):
    """设置地址标题"""
    def put(self, request, address_id):
        # 接收参数：地址标题
        json_dict = json.loads(request.body.decode())
        title = json_dict.get('title')
        try:
            # 查询地址
            address = Address.objects.get(id=address_id)

            # 设置新的地址标题
            address.title = title
            address.save()
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '设置地址标题失败'}, status=400)
        return JsonResponse({'code': 0, 'errmsg': '设置地址标题成功'})