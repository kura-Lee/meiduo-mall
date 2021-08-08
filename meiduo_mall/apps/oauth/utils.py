from itsdangerous import BadData
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings


class QQAuth:

    def __init__(self, security_key, expires=3600):
        self.security_key = security_key
        self.serializer = Serializer(security_key, expires_in=expires)

    def generate_access_token(self, openid_data):
        return self.serializer.dumps(openid_data).decode()

    def check_access_token(self, access_token):
        try:
            data = self.serializer.loads(access_token)
        except BadData:
            return
        else:
            return data.get('openid')


QQ_access_token = QQAuth(settings.SECRET_KEY)

