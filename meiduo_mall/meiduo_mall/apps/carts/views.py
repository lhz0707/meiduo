from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django_redis import get_redis_connection
import json, pickle, base64
from goods.models import SKU

# Create your views here.
class CartView(View):
    def post(self,request):

        # 保存購物車數據
        # 獲取前段觸底的數據
        data=request.body.decode()
        data_dict=json.loads(data)

        # 驗證數據
        sku_id=data_dict.get('sku_id')
        count=data_dict.get('count')
        selected=True
        try:
            sku=SKU.objects.get(id=sku_id)
        except:
            return JsonResponse({'error':'商品不存在'},status=400)
        if int(count)>sku.stock:
            return JsonResponse({'error':'庫存不足'},status=400)

        # 保存數據
        # 判斷用戶是否登陸
        user = request.user
        if user.is_authenticated:
            # 3-2登录用户 保存在redis
            client = get_redis_connection('carts')

            # 保存商品和數量 set hincrby 可以累加

            client.hincrby('carts_%s'%user.id,sku_id,count)
            # 判斷是否選中
            if selected:
                client.sadd('carts_selected_%d'%user.id,sku_id)
            return JsonResponse ({'code':'0'})

        else:
            # 未登陸用戶 hash 累心 key 屬性 值
            data_dict={}

            sku_data=data_dict.get(sku_id)
            if sku_data:
                # 如果獲取到商品數據count增加
                count+=sku_data['count']

            # 講新數據寫入字典
            data_dict[sku_id]={
                'count':count,
                'selected':selected
            }
            # 加密數據
            cart_cookie = base64.b64encode(pickle.dumps(data_dict)).decode()

            # 寫入cookie
            response=JsonResponse({'code':0})
            response.set_cookie('cart_cookie',cart_cookie,60*60*2)
            return  response

    def get(self,request):
        # 獲取夠哦無車數據
        user=request.user
        if user.is_authenticated:
            client=get_redis_connection('carts')
            sku_id_count=client.hgetall('carts_%d'%user.id)
            # 3-4获取选中状态的ku_id
            sku_id_selected = client.smembers('carts_selected_%d' % user.id)
            data_dict={}
            for sku_id,count in sku_id_count.items():
                data_dict[int(sku_id)]={
                    'count':int(count),
                    'selected':sku_id in sku_id_selected
                }
        else:
            # 未登陸用戶
            cart_cookie=request.COOKIES.get('cart_cookie')

            # 查看cookie中是否有數據
            if cart_cookie:
                data_dict=pickle.loads(base64.b64decode(cart_cookie))

            else:
                data_dict={}

            # 獲取所有商品的key直
        sku_keys=data_dict.keys()

        skus=SKU.objects.filter(id__in=sku_keys)
        cart_skus=[]
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': str(sku.price),
                'caption': sku.caption,
                'count': data_dict[sku.id]['count'],
                'selected': str(data_dict[sku.id]['selected']),
                'default_image_url': sku.default_image.url
            })

        return render(request, 'cart.html', {'cart_skus': cart_skus})

    # 更新購物車
    def put(self,request):

        # 獲取前段數據
        data=request.body.decode()
        data_dict=json.loads(data)

        # 雁陣數據
        sku_id =data_dict.get('sku_id')
        count=data_dict.get('count')
        selected=data_dict.get('selected')

        try:
            sku=SKU.objects.get(id=sku_id)
        except:
            return JsonResponse({'error':'商品不存在'},status=400)
        if int (count)>sku.stock:
            return JsonResponse({'error':'庫存不足'})

        user=request.user
        if user.is_authenticated:
            client=get_redis_connection('carts')

            # 跟新數據
            client.hset('carts_%s' % user.id, sku_id, count)
            if selected:
                client.sadd('cart_selected_%d',user.id,sku_id)
            else:
                client.srem('cart_selected_%D',user.id,sku_id)

            # 返回結果
            cart_sku={
                'id':sku_id,
                'name':sku.name,
                'price':str(sku.price),
                'caption':sku.caption,
                'count':count,
                'selected':str(selected),
                'default_image_url':sku.default_image.url
            }
            return  JsonResponse({'code':'0','cart_sku':cart_sku})
        else:
    # 未登陸
            cart_cookie=request.COOKIES.get('cart_cookie')
            if cart_cookie:
                data_dict=pickle.loads(base64.b64decode(cart_cookie))
            else:
                data_dict={}
            # 講數據跟新到字典
            data_dict[sku_id]={
                'count':count,
                'selected':selected
            }

            cart_sku={
                'id':sku.id,
                'name':sku.name,
                'price':str(sku.price),
                'caption':sku.caption,
                'count':count,
                'selected':str(selected),
                'default_image_url':sku.default_image.url
            }

        cart_cookie = base64.b64encode(pickle.dumps(data_dict)).decode()
        # 写入cookie
        response = JsonResponse({'code': 0, 'cart_sku': cart_sku})
        response.set_cookie('cart_cookie', cart_cookie, 60 * 60 * 2)

        return  response

        # 刪除購物車數據
    def delete(self,request):

        # 獲取數據
        data=request.body.decode()
        data_dict=json.loads(data)
        # 驗證數據
        sku_id=data_dict.get('sku_id')
        try:
            sku=SKU.objects.get(id=sku_id)

        except:
            return JsonResponse({'error':'商品不存在'},status=400)

        # 刪除數據
        user =request.user
        if user.is_authenticated:
            client=get_redis_connection('carts')

            # 刪除商品id count數量
            client.hdel('carts_%s'%user.id,sku_id)
            client.srem('carts_selected_%d' % user.id, sku_id)

            return JsonResponse({'code':'0'})

        else:

            # 未登陸用戶
            cart_cookie=request.COOKIES.get('cart_cookie')
            if cart_cookie:
                data_dict=pickle.loads(base64.b64decode(cart_cookie))

            else:
                return JsonResponse({'code':'0'})

            # 判斷當前id是否在cookiezhong
            if sku_id in data_dict.keys():
                del  data_dict[sku_id]


            # 加密
            cart_cookie = base64.b64encode(pickle.dumps(data_dict)).decode()
            response=JsonResponse({'code':0})
            response.set_cookie('cart_cookie',cart_cookie,69*690*2)

            return response

# 全選
class CartSelectionView(View):
    def put(self,request):
        data=request.body.decode()
        data_dict=json.loads(data)
        # 驗證數據
        selected=data_dict.get('selected')

        user=request.user
        if user.is_authenticated:
            client=get_redis_connection('carts')

            # 獲取所有商品id
            sku_id_count=client.hgetall('cart_%s'%user.id)
            sku_ids=sku_id_count.keys()

            if selected:
                client.sadd('carts_selected_%d' % user.id, *sku_ids)

            else:

                # 爲選中
                client.srem('carts_selected_%d' % user.id, *sku_ids)

            return JsonResponse({'code':0})

        else:
            cart_cookie=request.COOKIES.get('cart_cookie')

        if cart_cookie:
            data_dict=pickle.loads(base64.b64decode(cart_cookie))

        else:
            return JsonResponse({'code':0})

        for sku_id,sku_dict in data_dict.items():
            sku_dict['selected']=selected

        cart_cookie = base64.b64encode(pickle.dumps(data_dict)).decode()

        response=JsonResponse({'code':0})
        response.set_cookie('cart_cookie',cart_cookie,60*60*2)
        return response

# 獲取簡單的購物車數據
class CartSimpleView(View):
    def get(self,request):
        user=request.user
        if user.is_authenticated:
            client=get_redis_connection('carts')

            sku_id_count=client.hgetall('cart_%s'%user.id)

            sku_id_selected=client.smembers('carts_selected%d'%user.id)

            data_dict={}
            for sku_id,count in sku_id_count.items():
                data_dict[int(sku_id)]={
                    'count':int(count),
                    'selected':sku_id in sku_id_selected
                }

        else:
            cart_cookie=request.COOKIES.get('cart_cookie')

            if cart_cookie:
                data_dict=pickle.loads(base64.b64decode(cart_cookie))
            else:
                data_dict={}

                # 获取所有商品的key
        sku_keys = data_dict.keys()
        skus = SKU.objects.filter(id__in=sku_keys)
        cart_skus=[]
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': str(sku.price),
                'caption': sku.caption,
                'count': data_dict[sku.id]['count'],
                'selected': str(data_dict[sku.id]['selected']),
                'default_image_url': sku.default_image.url

            })

        return JsonResponse({'cart_skus':cart_skus})