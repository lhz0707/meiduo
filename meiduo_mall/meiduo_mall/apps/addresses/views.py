from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from addresses.models import Area,Address

from django.http import JsonResponse
from django.core.cache import cache
import json
import re
#展示當前的`收貨地址界面
class AddressView(View):
    def get(self,request):
        #查詢當前用戶的用戶地址
        user=request.user
        address_list=[]
        # 便利地址列表獲取所需要信息
        for address in address_list:
            address_list.append({
                'id':address.id,
                'receiver':address.receiver,
                'province':address.province.name,
                'city':address.city.name,
                'district':address.district.namem,
                'place':address.place,
                'mobile':address.mobile,
                'tel':address.tel,
                'email':address.email,
                'title':address.title
            })

        return render(request, 'user_center_site.html')

method_decorator(login_required,name='dispatch')
class AreasView(View):
    def get(self,request):

    #     獲取地區id 獲取省信息
        area_id=request.GET.get('area_id')
        if area_id is None:
            province_list=[]
            for province in province_list:
                province_list.append({
                    'id':province.id,
                    'name':province.name
                })
            cache.set('province_list',province_list,60*60*2)
        else:
            province_list=cache.get('province_list_%s'%area_id)
            if province_list is None:
                data=Area.objects.filter(parent_id=area_id)
                province_list=[]
                for province in data:
                    province_list.append({
                        'id':province.id,
                        'name':province.name
                    })
                cache.set('province_list_%s'%area_id,province_list,60*60*2)
        # 返回數據
        return JsonResponse({
            'code':'0',
            'province_list':province_list
        })

#     保存收貨地址
class AddressCreateView(View):
    def post(self,request):
        data = request.body.decode()
        data_dict = json.loads(data)
        receiver = data_dict.get('receiver')
        province_id = data_dict.get('province_id')
        city_id = data_dict.get('city_id')
        district_id = data_dict.get('district_id')
        place = data_dict.get('place')
        mobile = data_dict.get('mobile')
        tel = data_dict.get('tel')
        email = data_dict.get('email')

#       校驗數據
        if len(receiver)>20 or len(receiver):
            return JsonResponse({'code':'0'})

        if not re.match(r'1[3-9]\d{9}',mobile):
            return JsonResponse({'code':'4007'})

        if mobile is None or mobile =='':
            return JsonResponse({'code':'4007'})

        user=request.user
        # 保存數據

        address=Address.objects.create(user=user,receiver=receiver,province_id=province_id,
        city_id=city_id,district_id=district_id,place=place,mobile=mobile,email=email,title='')

        address_dict = {
            'id': address.id,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email,
        }
        # 4、返回结果
        return JsonResponse({'code': '0', 'address': address_dict})


    def put(self,request,pk):
        # 獲取前段的數據

        data=request.body.decode()
        data_dict=json.loads(data)
        recevier=data_dict.get('recevier')
        province_id=data_dict.get('province_id')
        city_id=data_dict.get('city_id')
        district_id=data_dict.get('district')
        place=data_dict.get('place')
        mobile=data_dict.get('mobile')
        tel=data_dict.get('tel')
        email=data_dict.get('email')
        # 校驗數據  收貨地址做多20個
        if len(recevier)>20 or len(recevier)<0:
            return JsonResponse({'code':'5001'})
        if not re.match(r'1[3-9]\d{9}',mobile):
            return JsonResponse({'code':'4007'})
        if mobile is None or mobile=="":
            return JsonResponse({'code':'4007'})

        # 更新數據

        address=Address.objects.get(id=pk)
        address.receiver=recevier
        address.province_id=province_id
        address.city_id=city_id
        address.district_id=district_id
        address.place=place
        address.mobile=mobile
        address.tel=tel
        address.email=email
        address.save()

        # 返回更新後的結果
        address_dict = {
            'id': address.id,
            'receiver': address.receiver,
            'province': address.province.name,
            'city': address.city.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email,
        }
        # 4、返回结果
        return JsonResponse({'code': '0', 'address': address_dict})

    def delete(self,request,pk):
        try:
            address=Address.objects.get(id=pk)
        except:
            return  JsonResponse({'code':'0'})

        # 邏輯刪除地址
        address.is_deleted=True
        address.save()

        return JsonResponse({'code':'0'})


# 默認收貨地址
class AddressDefaultView(View):
    def put(self,request,pk):
        try:
            address=Address.objects.get(id=pk)
        except:
            return  JsonResponse({'code':'address'})
        # 將當前用戶地址設置爲默認地址
        user=request.user
        user.default_address=address
        user.save()

        return  JsonResponse({'code':'0'})

    # 設置標題
class AddressTitleView(View):
    def put(self,request,pk):
        # 查看地址是否存在
        pass


