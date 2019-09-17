import json

from django.shortcuts import render
from django.views import View
# Django提供的分页类
from django.core.paginator import Paginator
from goods.models import  SKU, SKUSpecification, GoodsCategory,GoodsVisitCount
from django.http import JsonResponse
from django_redis import get_redis_connection

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
            skus=SKU.objects.filter(category_id=categorie_id).order_by('create_time')
        elif sort =='price':
            skus=SKU.objects.filter(category_id=categorie_id).order_by('price')

        # 按照銷量排序
        else:
            skus=SKU.objects.filter(category_id=categorie_id).order_by('sales')


        #分也
        #
        page=Paginator(skus,5)
        page_skus=page.page(page_num)

        data={
            # 平道分類  蜜毛包鞋 分頁後的上平數據 分類對象 當前頁數 總頁數 排序
            'categories':categories,
            'breadcrumb':breadcrumb,
            'page_skus':page_skus,
            'category':cat3,
            'page_num':page_num,
            'total_page':page.num_pages,
            'sort':sort
        }


        return render(request,'list.html',data)

class GoodsHotView(View):
    def get(self,request,categorie_id):
        # 獲取熱銷商品
        data=SKU.objects.filter(category_id=categorie_id).order_by('-sales')
        skus=data[0:3]

        hot_sku_list = []
        for sku in skus:
            hot_sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url

            })
        # 3、返回商品信息
        return JsonResponse({'hot_sku_list': hot_sku_list})

# 獲取搜索頁面
class GoodsSearchView(View):

    def get(self,request):
        # 获取查询关键字
        q=request.GET.get('q')

        # 根据关键字搜索数据库
        skus=SKU.objects.filter(name__contains=q)
        # 频道分类数据
        categories = get_categories()

        page = Paginator(skus, 5)
        page_skus = page.page(1)

        # 返回搜索结果

        data = {

            'categories': categories,  # 频道分类数据
            'page_skus': page_skus,  # 分页后的商品数据
            'page_num': 1,  # 当前页数
            'total_page': page.num_pages,  # 总页数
        }
        return render(request, 'search_list.html', data)

# 商品详情
class GoodsDetailView(View):
    def get(self,request,pk):

        # 商品频道分类数据渲染
        categories=get_categories()

        # 面包导航数据
        try:
            sku=SKU.objects.get(id=pk)
        except:
            return JsonResponse({'error':'错误'})

        cat3=GoodsCategory.objects.get(id=sku.category.id)

        cat2=cat3.parent
        cat1=cat2.parent

        # 制定一级标题的额外路径
        cat1.url=cat1.goodschannel_set.filter()[0].url

        # 面包蓝
        breadcrumb={}
        breadcrumb['cat1']=cat1
        breadcrumb['cat2']=cat2
        breadcrumb['cat3']=cat3

        # 规格和选项参数
        # 获取当前商品的规格参数
        spu=sku.spu
        specs=spu.specs.all()
        # 制定规格选项
        for spec in specs:
            # 获取当前所有的规格选项
            spec.option_list=spec.options.all()

            for option in spec.option_list:

                # 判断当前选项是否是当前商品
                if option.id ==SKUSpecification.objects.get(sku=sku,spec=spec).option_id:
                    option.sku_id = sku.id

                else:
                    other_good=SKU.objects.filter(specs__option_id=option.id)
                       # 查询当前商品的其他规格
                    sku_specs=SKUSpecification.objects.filter(sku=sku).exclude(sku=sku,spec=spec)

                    # 获取其他的规格数据
                    optionlist=[]
                    for sku_spec in sku_specs:
                        optionid=sku_spec.option_id
                        optionlist.append(optionid)

                    other_good1 = SKU.objects.filter(specs__option_id__in=optionlist)
                    good = other_good & other_good1
                    option.sku_id = good[0].id
        data = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'spu': spu,
            'category_id': sku.category.id,
            'specs': specs,
        }

        return render(request, 'detail.html', data)


#商品分类访问量
class GoodsVisitView(View):
    def post(self,request,pk):

        # 判断分类是否存在
        try:
            GoodsCategory.objects.get(id=pk)
        except:
            return  JsonResponse({'error':'错误'},status=400)

        # 判斷當前匪類是否保存過
        try:
            goodvisit=GoodsVisitCount.objects.get(category_id=pk)
        except:
            # 講沒有保存過的數據進行保存
            GoodsVisitCount.objects.create(category_id=pk,count=1)
            return JsonResponse({'massage':'ok'})

        # 商品瀏覽量技術
        goodvisit.count+=1
        goodvisit.save()

        return JsonResponse({'massage':'ok'})


class GoodsHistoryView(View):
    def post(self,request):
        # 用戶瀏覽歷史數據

        # 獲取前段傳入的sku_id 數據
        data=request.body.decode()
        data_dict=json.loads(data)

        # 驗證sku_id所對應的商品是否存在
        sku_id=data_dict.get('sku_id')
        try:
            SKU.objects.get(id=sku_id)
        except:
            return JsonResponse({'error':'錯誤'},status=400)

        # 獲取當前鄧麗的用戶
        user=request.user

        # 鏈接redis
        client=get_redis_connection('history')

        # 判斷當親書庫——id 是否已經存儲過 觸怒出國則刪除
        client.lrem('history_%s'%user,0,sku_id)

        # 講互獲取的數據存儲到redis數據哭中
        client.lpush('history_%s'%user,0,sku_id)

        # 控制截取數量
        client.ltrim('history_%s'%user,0,5)
        # 返回結果
        return JsonResponse({'message':'ok'})



    def get(self,request):
        # 獲取當前用戶
        user=request.user
        # 鏈接redis
        client=get_redis_connection('history')

        # 提起商品分類的數據
        skus_ids=client.lrange('history_%s'%user,0,-1)

        # 根據商品id查詢數據
        skus=SKU.objects.filter(id__in=skus_ids)
        sku_list=[]
        for sku in skus:
            sku_list.append({

                'id':sku.id,
                'name':sku.name,
                'default_image_url':sku.default_image.url,
                'price':sku.price
            })
        #     講產訊到的是你高頻數據進行返回
        return JsonResponse({'skus':sku_list})