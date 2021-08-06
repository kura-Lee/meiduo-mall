import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList
from apps.users.models import User

def vaild_mobile(mobile):
    if not re.match('1[3-9]\d{9}', mobile):
        raise ValidationError('请输入正确的手机号')


class RegisterForm(forms.Form):

    # def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
    #              initial=None, error_class=ErrorList, label_suffix=None,
    #              empty_permitted=False, field_order=None, use_required_attribute=None, renderer=None, request=None):
    #     super().__init__(data, files, auto_id, prefix,initial, error_class, label_suffix,
    #                    empty_permitted, field_order, use_required_attribute, renderer)
    #     self.request = request

    username = forms.CharField(min_length=5, max_length=20, error_messages={'required': '请输入用户名', 'max_length': '用户名在5-20位', 'min_length': '用户名在5-20位'})
    password = forms.CharField(min_length=8, max_length=20, error_messages={'required': '请输入密码', 'max_length': '密码在8-20位', 'min_length': '密码在8-20位'})
    password2 = forms.CharField(min_length=8, max_length=20, error_messages={'required': '请输入确认密码', 'max_length': '确认密码在8-20位', 'min_length': '确认密码在8-20位'})
    mobile = forms.CharField(min_length=11, max_length=11, validators=[vaild_mobile], error_messages={'required': '请输入手机号', 'max_length': '请输入正确的手机号', 'min_length': '请输入正确的手机号'})
    sms_code = forms.CharField(error_messages={'required': '请输入验证码'})
    allow = forms.CharField(error_messages={'required': '请勾选用户协议'})

    def clean_username(self):
        print('requset')
        print(self.request)
        print('requset')
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).first():
            raise ValidationError('用户名已存在')
        else:
            return username

    def clean(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise ValidationError({'password2': '两次输入的密码不一致'})
        else:
            return self.cleaned_data