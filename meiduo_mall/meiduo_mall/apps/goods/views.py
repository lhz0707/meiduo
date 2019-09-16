from django.shortcuts import render
from django.views import View
# Django提供的分页类
from django.core.paginator import Paginator
from goods.models import GoodsCategory, SKU
from django.http import JsonResponse

# Create your views here.
from contents.utils import get_categories


class GoodsListView(View):

    def get(self,request,categorie_id,page_num):
        categories=get_categories()
        # 渲染密保寫導航數據
        # 面包屑导航数据
        cat3 = GoodsCategory.objects.get(id=categorie_id)
        cat2 = cat3.parent
        cat1 = cat2.parent
        # 一级分类额外指定url路径
        cat1.url = cat1.goodschannel_set.filter()[0].url
        breadcrumb = {}
        breadcrumb['cat1'] = cat1
        breadcrumb['cat2'] = cat2
        breadcrumb['cat3'] = cat3

        # 渲染當前分類下的所有上平
        # 獲取排序字段
        sort=request.GET.get('sort')
        if sort is None or sort=='create_time':
            sort='create_time'
        #     默認排序
            skus=SKU.objects.filter(categorie_id=categorie_id).order_by('create_time')
        elif sort =='price':
            skus=SKU.objects.filter(categorie_id=categorie_id).order_by('price')

        # 按照銷量排序
        else:
            skus=SKU.objects.filter(category_id=categorie_id).order_by('sales')


        #分也

        page=Paginator(skus,5)
        page_skus=page.page(page_num)

        data={
            # 平道分類  蜜毛包鞋 分頁後的上平數據 分類對象 當前頁數 總頁數 排序
            'categories':categories,
            'breadcrumb':breadcrumb,
            'page_skus':page_skus,
            'cat3':cat3,
            'page_num':page_num,
            'num_pages':page.num_pages,
            'sort':sort
        }


        return render(request,'list.html',data)