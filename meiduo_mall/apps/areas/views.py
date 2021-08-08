from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from apps.areas.models import Area
from django.core.cache import cache
import logging

from utils.views import LoginRequiredJSONMixin

logger = logging.getLogger('django')



class AreasView(LoginRequiredJSONMixin, View):
    """
    省的查询
    """
    def get(self, request):
        try:
            province_list = cache.get('province')
            if province_list is None:
                provinces = Area.objects.filter(parent=None)
                province_list = []
                for province in provinces:
                    province_list.append({"id": province.id, "name": province.name})
                # 缓存数据到redis
                cache.set('province', province_list, 24 * 3600)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '省份数据错误'})
        return JsonResponse({'code': 0, "errmsg": "OK", "province_list": province_list})


class SubAreasView(LoginRequiredJSONMixin, View):
    """
    市区县的查询
    """
    def get(self, request, pk):
        try:
            sub_data = cache.get('sub_data:%s' % pk)
            if sub_data is None:
                up = Area.objects.get(id=pk)
                downs = Area.objects.filter(parent=pk)
                sub_list=[]
                for down in downs:
                    sub_list.append({'id': down.id, 'name': down.name})
                sub_data = {
                    'id': up.id,
                    'name': up.name,
                    'subs': sub_list
                }
                # 缓存数据
                # cache.set(key,value,expire)
                cache.set('sub_data:%s' % pk, sub_data, 24 * 3600)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '数据错误'})
        return JsonResponse({'code': 0, "errmsg": 'ok', "sub_data": sub_data})



