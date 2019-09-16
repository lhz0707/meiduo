from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from addresses.models import Area,Address
from django.http import JsonResponse
from django.core.cache import cache
import json
import re


# Create your views here.
@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        # 查询当前用户的地址信息
        user = request.user
        addresses = Address.objects.filter(user=user, is_deleted=False)
        addresses_list = []
        for address in addresses:
            addresses_list.append({
                'id': address.id,
                'receiver': address.receiver,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'mobile': address.mobile,
                'tel': address.tel,
                'email': address.email,
                'title':address.title,
        #         , {'addresses': addresses_list}
            })

        return render(request, 'user_center_site.html',{'addresses': addresses_list})


@method_decorator(login_required, name='dispatch')
class AreasView(View):
    def get(self,request):

        # 获取area_id
        area_id=request.GET.get('area_id')
        if area_id is None:
            province_list = cache.get('province_list')
            if province_list is None:
                # 1、查询省市区数据库获取省信息
                data = Area.objects.filter(parent_id=area_id)
                province_list = []
                for province in data:
                    province_list.append({
                        'id': province.id,
                        'name': province.name
                    })
                cache.set('province_list', province_list, 60 * 60 * 2)

        else:
            province_list = cache.get('province_list_%s' % area_id)
            if province_list is None:
                data = Area.objects.filter(parent_id=area_id)
                province_list = []
                for province in data:
                    province_list.append({
                        'id': province.id,
                        'name': province.name
                    })
                cache.set('province_list_%s' % area_id, province_list, 60 * 60 * 2)

        # 返回数据
        return JsonResponse({
            'code': '0',
            'province_list': province_list
        })

@method_decorator(login_required, name='dispatch')
class AddressCreateView(View):
    def post(self,request):
    #     獲取前段數據
        data_dict=json.loads(data=request.body.decode())
        receiver=data_dict.get('recevier')
        province_id=data_dict.get('province_id')
        city_id=data_dict.get('city_id')
        district_id=data_dict.get('district')
        place=data_dict.get('place')
        mobile=data_dict.get('mobile')
        tel=data_dict.get('tel')
        email=data_dict.get('email')

    #    驗證書局
        if len(receiver)>20 or len(receiver)<0:
            return  JsonResponse({'code':'5001'})
        if not re.match(r'1[3-9]\d{9}]',mobile):
            return JsonResponse({'code': '4007'})
        user=request.user

        address = Address.objects.create(user=user, receiver=receiver, province_id=province_id, city_id=city_id,
                                     district_id=district_id, place=place, mobile=mobile, tel=tel, email=email)

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
    def put(self, request, pk):
        # 1、获取前端数据
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

        # 2、验证数据
        if len(receiver) > 20 or len(receiver) < 0:
            return JsonResponse({"code": 5001})
        if not re.match(r'1[3-9]\d{9}', mobile):
            return JsonResponse({"code": 4007})
        if mobile is None or mobile == '':
            return JsonResponse({"code": 4007})

        # 3、更新数据
        address = Address.objects.get(id=pk)
        address.receiver = receiver
        address.province_id = province_id
        address.city_id = city_id
        address.district_id = district_id
        address.place = place
        address.mobile = mobile
        address.tel = tel
        address.email = email
        address.save()

        # 4、返回结果
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

    def delete(self, request, pk):
        """
            删除数据
        :param request:
        :return:
        """
        # 1、根据id查询地址数据
        try:
            address = Address.objects.get(id=pk)
        except:
            return JsonResponse({"code": 5001})
        # 2、逻辑删除地址
        address.is_deleted = True
        address.save()
        # 3、返回结果
        return JsonResponse({'code': '0'})


class AddressDefaultView(View):


    def put(self, request, pk):
        # 1、查询地址是否存在
        try:
            address = Address.objects.get(id=pk)
        except:
            return JsonResponse({"code": 5001})
        # 2、将当前地址设置为用户默认地址
        user = request.user
        user.default_address = address
        user.save()

        # 3、返回结果
        return JsonResponse({'code': 0})


class AddressTitleView(View):
    """
        设置标题
    """

    def put(self, request, pk):
        # 1、查询地址是否存在
        try:
            address = Address.objects.get(id=pk)
        except:
            return JsonResponse({"code": 5001})
        # 2、将当前地址设置为用户默认地址
        title = json.loads(request.body.decode()).get('title')
        address.title = title
        address.save()

        # 3、返回结果
        return JsonResponse({'code': 0})
