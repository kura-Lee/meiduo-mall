from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings

def generate_verify_email_url(user):
    """
    生成邮箱验证链接
    :param user: 当前登录用户
    :return: verify_url
    """
    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    data = {'user_id': user.id, 'email': user.email}
    token = serializer.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
    return verify_url

def check_verify_email_url(token):
    serializer = Serializer(settings.SECRET_KEY)
    try:
        data = serializer.loads(token)
    except BadData:
        return
    else:
        return data
