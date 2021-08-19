from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageNum(PageNumberPagination):
    """查询用户分页类"""
    # 开启分页，设置默认分页一页5条
    page_size = 5
    # 设置可通过参数传递实现分页条数
    page_query_param = 'page'
    page_size_query_param = 'pagesize'
    # 设置一页最大条数
    max_page_size = 20

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('lists', data),
            ('page', self.page.number),
            ('pages', self.page.paginator.num_pages),
            ('pagesize', self.page.paginator.per_page),
        ]))