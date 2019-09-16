from django.shortcuts import render
from django.views import View
from goods.models import SKU
from collections import OrderedDict
from goods.models import GoodsChannel
from contents.models import ContentCategory
from django.http import JsonResponse,HttpResponse
from contents.utils import get_categories

# Create your views here.
class IndexView(View):
    # 渲染首頁關高數據
    def get(self,request):
        # 渲染分類導航數據
        categories = get_categories()

        contents = {}
        # 查询所有广告分类
        contentcategorys = ContentCategory.objects.all()
        for contentcategory in contentcategorys:
            contents[contentcategory.key] = contentcategory.content_set.filter(status=True).order_by('sequence')

        data = {
            'categories': categories,
            'contents': contents
        }

        return render(request, 'index.html', data)





