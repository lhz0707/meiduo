from collections import OrderedDict

from goods.models import GoodsChannel


def get_categories():
    # 生成一个有序的字典
    categories = OrderedDict()
    # 查询分组频道表
    channels = GoodsChannel.objects.all().order_by('group_id', 'sequence')
    for channel in channels:
        # 获取分组编号
        group_id = channel.group_id
        # 判断分组编号是否已经存在
        if group_id not in categories:
            categories[group_id] = {'channels': [], 'sub_cats': []}

        # 获取一级分类对象
        cat1 = channel.category
        categories[group_id]['channels'].append(
            {
                'id': cat1.id,
                'name': cat1.name,
                'url': channel.url
            }
        )
        # 获取二级分类
        cat2s = cat1.subs.all()
        for cat2 in cat2s:
            cat2.sub_cats = []
            for cat3 in cat2.subs.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)
    return categories