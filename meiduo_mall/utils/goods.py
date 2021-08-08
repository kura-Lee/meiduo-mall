from collections import OrderedDict
from apps.goods.models import GoodsChannel

def get_categories():
    """
    提供商品频道和分类
    :return 菜单字典
    """
    categories = OrderedDict()
    # 先按组排序，然后以具体分类的顺序排序
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in channels:
        # 当前组的id
        group_id = channel.group_id
        # 按照group_id创建最外层的字典
        # {group_id:{"channels": [], "sub_cats": []}}
        if group_id not in categories:
            categories[group_id] = {"channels": [], "sub_cats": []}
        # 查询其外键category获取当前sequence的一级分类
        cat1 = channel.category
        categories[group_id]["channels"].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })
        # 通过自连接的一级分类查询二级分类
        for cat2 in cat1.subs.all():
            cat3_list = []
            # 查询二级分类的三级分类
            for cat3 in cat2.subs.all():
                cat3_list.append({
                    "id": cat3.id,
                    "name": cat3.name
                })
            categories[group_id]["sub_cats"].append({
                "id": cat2.id,
                "name": cat2.name,
                "sub_cats": cat3_list
            })
    return categories


def get_breadcrumb(category):
    """
    三级面包屑导航
    :param category: 第三级分类的商品模型实例
    :return: 面包屑导航字典
    """
    breadcrumb = dict(
        cat1='',
        cat2='',
        cat3=''
    )
    if category.parent is None:
        breadcrumb['cat1'] = category.name
    elif category.parent.parent is None:
        breadcrumb['cat1'] = category.parent.name
        breadcrumb['cat2'] = category.name
    else:
        breadcrumb['cat3'] = category.name
        breadcrumb['cat2'] = category.parent.name
        breadcrumb['cat1'] = category.parent.parent.name
    return breadcrumb

def get_goods_specs(sku):
    """构建当前商品的规格键"""
    # 构建当前商品的规格键        (具体选项id)
    sku_specs = sku.specs.order_by('spec_id')
    sku_key = []
    for spec in sku_specs:
        sku_key.append(spec.option.id)

    # 获取当前商品的所有SKU
    skus = sku.spu.sku_set.all()
    # 构建不同规格参数的sku字典        （选项类别）
    spec_sku_map = {}
    for s in skus:
        # 获取sku的规格参数
        s_specs = s.specs.order_by('spec_id')
        # 用于形成规格参数-sku字典的键      (具体选项)
        key = []
        for spec in s_specs:
            key.append(spec.option.id)
        # 向规格参数-sku字典添加记录
        spec_sku_map[tuple(key)] = s.id

    # 以下代码为：在每个选项上绑定对应的sku_id值
    # 获取当前商品的规格信息
    goods_specs = sku.spu.specs.order_by('id')
    # 若当前sku的规格信息不完整，则不再继续
    if len(sku_key) < len(goods_specs):
        return
    for index, spec in enumerate(goods_specs):
        # 复制当前sku的规格键
        key = sku_key[:]
        # 该规格的选项
        spec_options = spec.options.all()
        for option in spec_options:
            # 在规格参数sku字典中查找符合当前规格的sku
            key[index] = option.id
            option.sku_id = spec_sku_map.get(tuple(key))
        spec.spec_options = spec_options
    # print(goods_specs)
    return goods_specs
