from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django_redis import get_redis_connection
from random import randint

from meiduo_mall.libs.captcha.captcha import Captcha
from celery_tasks.yuntongxun.sms import CCP
from users.models import User
from celery_tasks.code_sms.tasks import send_sms_code
from threading import Thread



# Create your views here.
class ImgaeView(View):
    """
        图片验证码
    """

    def get(self, request, uuid):
        # 1、生成图片验证
        captcha = Captcha.instance()
        data, text, image = captcha.generate_captcha()
        # 2、将图片验证码存储到服务器reids
        client = get_redis_connection('verfycode')
        client.setex('image_code_%s' % uuid, 60 * 5, text)
        # 3、返回验证码图片
        return HttpResponse(image, content_type='image/jpg')


class SmsCodeView(View):
    def get(self, request, mobile):
        client = get_redis_connection('verfycode')
        # 判断两次请求的时间间隔是否在60s内容
        flag_data = client.get('sms_flag_%s' % mobile)
        if flag_data:
            return HttpResponse('请求过于频繁', status=400)
        # 1、获取前端数据
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        # 2、生成短信验证码
        sms_code = '%06d' % randint(0, 999999)
        print(sms_code)
        # 3、验证图片验证码
        client = get_redis_connection('verfycode')
        real_code = client.get('image_code_%s' % uuid)
        if real_code is None:
            return HttpResponse('图片验证码失效', status=400)
        if image_code.lower() != real_code.decode().lower():
            return HttpResponse('输入验证码错误')
        # 4、发送短信
        # ccp = CCP()
        # ccp.send_template_sms(mobile, [sms_code, '5'], 1)
        # t=Thread(target=send_sms_code,args=(mobile,sms_code))
        # t.start()
        # 调用celery的异步任务完成发送短信
        send_sms_code.delay(mobile,sms_code)

        # 5、保存生成的短信验证码到redis
        # 开启redis管道
        pipline=client.pipeline()
        pipline.setex('sms_code_%s' % mobile, 60 * 5, sms_code)
        pipline.setex('sms_flag_%s' % mobile, 60, 123)
        # 使用管道发送数据
        pipline.execute()

        # 6、返回结果
        return JsonResponse({'code': '0'})


class UsernameCount(View):
    """
        判断用户名是否重复
    """
    def get(self,request,username):
        # 1、获取前端传递的用户名
        # 2、查询用户名所对应对象数量
        count=User.objects.filter(username=username).count()
        # 3、返回查询到数量
        return JsonResponse({'count':count})

class MobileCount(View):
    """
        判断手机号是否重复
    """

    def get(self, request, mobile):
        # 1、获取前端传递的用户名
        # 2、查询用户名所对应对象数量
        count = User.objects.filter(mobile=mobile).count()
        # 3、返回查询到数量
        return JsonResponse({'count': count})




# class TestView(View):
#
#
#     def get(self,requst):
#
#         return render(requst,'testajax.html')
#
#
# class UserView(View):
#
#     def get(self,request):
#
#         return HttpResponse('python',status=400)
