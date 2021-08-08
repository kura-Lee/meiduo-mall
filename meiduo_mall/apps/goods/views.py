from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from collections import OrderedDict

from apps.contents.models import ContentCategory
from apps.goods.models import GoodsChannel, GoodsCategory, SKU
from utils.goods import get_categories, get_breadcrumb


class IndexView(View):
    """
    首页，包含商品分类和广告数据两部分
    """

    def get(self, request):
        # 查询商品频道和分类
        categories = get_categories()

        # 广告数据
        contents = {}
        # 查询所有的广告分类
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        context = {
            'categories': categories,
            'contents': contents,
        }
        # 模板渲染，静态页面
        return render(request, 'index.html', context)
        # return JsonResponse(context)


class ListView(View):
    """
    商品列表 包含
        商品频道分类
        面包屑导航
        排序和分页
    """
    def get(self, request, category_id):
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        ordering = request.GET.get('ordering')
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '页面错误'}, status= 400)
        # 查询面包屑导航数据
        breadcrumb = get_breadcrumb(category)
        # 查询已经上架的此三级子类别商品
        try:
            skus = SKU.objects.filter(category=category_id, is_launched=True).order_by(ordering)
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '页面错误'}, status=400)
        paginator = Paginator(skus, page_size)
        # 获取列表页总页数
        total_page = paginator.num_pages
        page_skus = paginator.page(page)
        sku_list = []
        # 将对象转换为字典数据
        for sku in page_skus.object_list:
            sku_list.append({
                "id": sku.id,
                'name': sku.name,
                'price': sku.price,
                # 注意这里加上url，调用自定义存储类的url方法
                'default_image_url': sku.default_image.url
            })
        return JsonResponse({
            'code': 0,
            'errmsg': 'ok',
            'breadcrumb': breadcrumb,
            'list': sku_list,
            'count': total_page
        })


class HotGoodsView(View):
    """商品热销排行"""

    def get(self, request, category_id):
        """提供商品热销排行JSON数据"""
        # 据路径参数category_id查询出该类型商品销量前二的商品。
        # 验证分类category_id是否存在
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '页面错误'}, status=400)
        # 查询已经上架的此三级子类别商品
        skus = SKU.objects.filter(category=category_id, is_launched=True).order_by("sales")[:2]
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                "id": sku.id,
                "default_image_url": sku.default_image.url,
                "name": sku.name,
                "price": sku.price
            })

        return JsonResponse({'code': 0, 'errmsg': 'OK', 'hot_skus': hot_skus})


from haystack.views import SearchView


class MySearchView(SearchView):
    '''重写SearchView类'''

    def create_response(self):
        """重写返回响应的方法"""
        # 获取搜索结果
        context = self.get_context()
        data_list = []
        for sku in context['page'].object_list:
            data_list.append({
                'id': sku.object.id,
                'name': sku.object.name,
                'price': sku.object.price,
                'default_image_url': sku.object.default_image.url,
                'searchkey': context.get('query'),
                'page_size': context['page'].paginator.num_pages,
                'count': context['page'].paginator.count
            })
        # 拼接参数, 返回
        return JsonResponse(data_list, safe=False)


from utils.goods import get_goods_specs

class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """提供商品详情页"""
        # 获取当前sku的信息
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')
        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)
        # 查询SKU规格信息
        goods_specs = goods_specs = get_goods_specs(sku)

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }
        return render(request, 'detail.html', context)


from apps.goods.models import GoodsVisitCount
from datetime import date


class DetailVisitView(View):
    """详情页分类商品访问量"""
    def post(self, request, category_id):
        try:
            # 1.获取当前商品
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        # 2.查询日期数据
        # 获取当天日期
        today_date = date.today()
        try:
            # 3.如果有当天商品分类的数据  就累加数量
            count_data = category.goodsvisitcount_set.get(date=today_date)
        except:
            # 4. 没有, 就新建之后在增加
            count_data = GoodsVisitCount()

        try:
            count_data.count += 1
            count_data.category_id = category_id
            count_data.save()
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '新增失败'})
        return JsonResponse({'code': 0, 'errmsg': 'OK'})