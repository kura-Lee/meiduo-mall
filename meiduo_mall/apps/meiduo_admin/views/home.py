"""
首页视图
"""


from datetime import date, timedelta

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User


class DailyActiveAPIView(APIView):
    """日活统计"""
    def get(self, request):
        today = date.today()
        count = User.objects.filter(last_login__gte=today).count()
        return Response({'count': count})

class DailyOrderCountAPIView(APIView):
    """日下单用户统计"""
    def get(self, request):
        today = date.today()
        count = User.objects.filter(orderinfo__create_time__gte=today).count()
        return Response({'count': count})


class UserCountAPIView(APIView):
    """用户总量统计"""
    def get(self, request):
        today = date.today()
        count = User.objects.count()
        return Response({'date': today, 'count': count})


class DailyUserIncreAPIView(APIView):
    """单日用户增量统计"""
    def get(self, request):
        today = date.today()
        count = User.objects.filter(date_joined__gte=today).count()
        return Response({'date': today, 'count': count})


class MonthUserIncreAPIView(APIView):
    """月用户增量统计"""
    def get(self, request):
        now_date = date.today()
        start_date = now_date - timedelta(days=30)
        date_list = []
        for i in range(30):
            today = start_date + timedelta(days=i)
            next_day = today + timedelta(days=1)
            day_count = User.objects.filter(date_joined__gte=today, date_joined__lt=next_day).count()
            date_list.append({'date': today, 'count': day_count})
        return Response(date_list)


