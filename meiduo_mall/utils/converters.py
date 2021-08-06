from django.urls import converters

# Username路由转换器
class UsernameConvert:
    regex = '[0-9a-zA-Z_-]{5,20}'

    def to_python(self, value):
        return value

class MobileConvert:
    regex = '1[3-9]\d{9}'

    def to_python(self, value):
        return str(value)