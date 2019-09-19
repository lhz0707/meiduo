import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.db import transaction
from django_redis import get_redis_connection
from addresses.models import Address
from datetime import datetime
from decimal import Decimal

# Create your views here.
from goods.models import SKU
from orders.models import OrderInfo, OrderGoods



# Create your views here
@method_decorator(login_required,name='dispatch')
class OrderView(View):
    def get(self,request):
        # 渲染地址
        user=request.user
        addresses=Address.objects.filter(user=user,is_deleted=False)
        # 商品数据渲染
        client=get_redis_connection('carts')
        # 获取商品数量
        sku_id_count=client.hgetall('carts_%s'%user.id)
        sku_count={}
        for sku_id,count in sku_id_count.items():
            sku_count[int(sku_id)]=int(count)
        # 获取选中的sku_id
        sku_ids =client.smembers('carts_selected_%d'%user.id)
        skus=SKU.objects.filter(id__in=sku_ids)
        sku_list=[]
        total_count=0
        total_amount=0
        for sku in skus:
            sku_list.append({
                'default_image_url':sku.default_image.url,
                'name':sku.name,
                'price':sku.price,
                'count':sku_count[sku.id],
                'total_amount':sku_count[sku.id]*sku.price
            })
            # 累加商品的数量
            total_count+=sku_count[sku.id]

            # 累加商品的价格
            total_amount+=sku_count[sku.id]*sku.price

            # 运费
        transit=10
            # 总金额
        payment_amount=total_amount+transit

        data = {
            'addresses': addresses,
            'sku_list': sku_list,
            'total_count': total_count,
            'total_amount': total_amount,
            'transit': transit,
            'payment_amount': payment_amount
        }

        return render(request,'place_order.html',data)



# 保存 订单数据
class OrderCommitView(View):
    def post(self,request):
        data=request.body.decode()
        data_dict=json.loads(data)

        address_id=data_dict.get('address_id')
        pay_method=data_dict.get('pay_method')
        try:
            address=Address.objects.get(id=address_id)
        except:
            return  JsonResponse({'error':'地址不存在'},status=400)

        # 获取当前用户对象
        user=request.user
        # 生成订单id
        order_id=datetime.now().strftime('%Y%m%d%H%M%S')+'%09d'%user.id
        # 开启事物
        with transaction.atomic():
            # 设置保存点
            save_point=transaction.savepoint()
            try:
                # 初始话生成订单的基本信息
                order=OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal(0),
                    freight=Decimal(10),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']if pay_method==OrderInfo.PAY_METHODS_ENUM[
                        'ALPAY']else
                    OrderInfo.ORDER_STATUS_ENUM['USERND']
                )
            # 查询商品的选中状态
                client=get_redis_connection('carts')
                sku_id_count=client.hgetall('carts_%s'%user.id)
                sku_count={}

                # 获取商品的数量
                for sku_id,count in sku_id_count.items():
                    sku_count[int[sku_id]]=int(count)
                # 获取选中的sku_id
                sku_ids=client.smembers('carts_selected_%d'%user.id)

                # 循环列表获取处理的商品地订单
                for sku_id in sku_ids:
                    while True:
                        # 获取当前商品的库存
                        sku=SKU.objects.get(id=sku_id)
                        stock_old=sku.stock
                        sales_old=sku.sales
                        # 判断购买的数量是否超过库存
                        if count >stock_old:
                            return JsonResponse({'message':'库存不足'},status=400)

                        # 修改sku商品的库存和销量
                        stock_new=sku.stock-count
                        sales_new=sku.sales+count

                        # 判断库存的数据
                        res=SKU.objects.filter(id=sku_id,stock=stock_old).update(stock=stock_new,sales=sales_new)
                        if res==0:
                            continue
                        # 修改spu表中的数据
                        sku.spu.sales+=count
                        # 累加订单数量
                        order.total_count+=count
                        # 累加订单价格
                        order.total_amount+=sku.price*count

                        # 保存订单的数据`
                        OrderGoods.objects.create(

                            order=order,
                            sku=sku,
                            count=count,
                            price=sku.price
                        )
                        break
                # freight 寄送货物
                order.total_amount+=order.freight
                order.save()
            except:
                # 回滚到保存点
                transaction.savepoint_rollback(save_point)
                return  JsonResponse({'error':'保存失败'},status=400)

            else:
                # 异常提交
                transaction.savepoint_commit(save_point)
                client.hdel('cart_%s'%user.id*sku_ids)
                client.srem('carts_selected_%d'%user.id,*sku_ids)
                return JsonResponse({'code':0,'order_id':order_id})


# 获取订单成功界面
class OrderSuccessView(View):
    def get(self,request):
        order_id=request.GET.get('order_id')
        payment_amount=request.GET.get('payment_amount')
        pay_method=request.GET.get('pay_method')
        data={
            'ordere_id':order_id,
            'payment_amount':payment_amount,
            'pay_method':pay_method
        }

        return render(request,'order_success.html',data)


# 用户中心获取当前用户的订单数据

class OrderInfoView(View):
    # 获取当前用户
    def get(self,request,pk):
        user=request.user
        orders=OrderInfo.objects.filter(user=user)

        # 订单商品
        for order in orders:
            order.details=[]
            # 获取订单商品
            order_goods=order.skus.all()
            for order_good in order_goods:
                order.details.append({
                    'default_image_url':order_good.sku.default_image.url,
                    'price':order_good.sku.price,
                    'name':order_good.sku.name,
                    'count':order_good.count,
                    'total_amount':order_good.count*order_good.sku.price
                })

        page=Paginator(orders,5)
        order_pages=page.page(pk)
        data={
            'page':order_pages,
            'page_num':pk,
            'total_page':page.num_pages,
        }
        return render(request,'user_center_order.html',data)

class OrderCommentView(View):
    # 获取订单评价页面
    def get(self,request):
        order_id=request.GET.get('order_id=order_id')

        # 根据订单查询商品信息
        try:
            order=OrderInfo.objects.get(order_id=order_id)
        except:
            return render(request,{'404.html'})
        goods_order=order.skus.filter(is_commented=False)

        # 渲染构建数据内容
        skus=[]
        for good in goods_order:
            skus.append({
                'name': good.sku.name,
                'price': str(good.price),
                'count': good.count,
                'comment': good.comment,
                'score': good.score,
                'is_anonymous': str(good.is_anonymous),
                'is_commented': str(good.is_commented),
                'default_image_url': good.sku.default_image.url,
                'order_id': order_id,
                'sku_id': good.sku.id
            })
        data={'skus':skus}

        return render(request,'goods_judge.html',data)

    def post(self,request):
        # 保存订单数据
        # 获取数据
        data=request.body.decode()
        data_dict=json.loads(data)
        # 验证数据
        sku_id=data_dict.get('sku_id')
        order_id=data_dict.get('order_id')
        comment=data_dict.get('comment')
        score=data_dict.get('score')
        is_anonymous=data_dict.get('is_anonymous')
        try:
            sku=SKU.objects.get(id=sku_id)
        except:
            return JsonResponse({'error': '商品不存在'}, status=400)
        try:
            OrderInfo.objects.get(order_id=order_id)
        except:
            return JsonResponse({'error': '订单不存在'}, status=400)
        # 3、保存评价信息
        OrderGoods.objects.filter(order=order_id, sku=sku).update(comment=comment, score=score,
                                                                      is_anonymous=is_anonymous, is_commented=True)
        return  JsonResponse({'code':0})