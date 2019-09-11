from django.shortcuts import render,redirect
from django.views import View
# 发送邮件的方法
from django.core.mail import send_mail
from django.contrib.auth import login,authenticate,logout
from django.http import HttpResponse,JsonResponse
from users.models import User
from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer as TJS
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.decorators import method_decorator
import re
import json
# Create your views here.
# 注册首页的模型类
class IndexView(View):

    def get(self,request):

        return render(request,'index.html')

# 用户注册
class UserRegisterView(View):
    # 获取用户的注册页面
    def get(self, request):

        return render(request, 'register.html')


    def post(self,request):
        # 获取前段传递的数据
        data = request.POST
        username = data.get('user_name')
        pwd1 = data.get('pwd')
        pwd2 = data.get('cpwd')
        mobile = data.get('phone')
        image_code = data.get('pic_code')
        sms_code = data.get('msg_code')
        allow = data.get('allow')
        # 验证表单数据
        # 验证表单数据否存在
        if username is None or pwd1 is None or pwd2 is None or mobile is None or image_code is None or sms_code is None or allow is None:
            return render(request, 'register.html', {'error_message': '数据不能为空'})
        # 验证用户名的长度
        if len(username)<5 or len(username)>20:
            return HttpResponse(request,'register.html',{'error_message': '用户名的长度错误'})

        # 用户名支持用手机号注册
        if re.match(r'1[3-9]\d{9}',username):
            if username!=mobile:
                return HttpResponse(request, 'register.html', {'error_message': '用户名和手机号不一致'})

        # 验证用户名是否存在
        try:
            user=User.objects.get(username=username)
        except:
            user=None

        # 如果用户名已存在


        # 验证输入的密码是否一致
        if pwd1!=pwd2:
            return HttpResponse(request, 'register.html', {'error_message': '两次输入的密码不一致'})

        # 验证手机号的格式
        if not re.match(r'1[3-9]\d{9}',mobile):
            return HttpResponse(request, 'register.html', {'error_message': '手机号的格式不正确'})

        # 验证短信验证码的长度
        if len(sms_code)!=6:
            return HttpResponse(request, 'register.html', {'error_message': '短信验证码的长度超出范围'})


        # 取出redis数据库中保存的手机号对应的验证码
        client=get_redis_connection('verfycode')
        real_sms_code=client.get('sms_code_%s'%mobile)

        # 判断验证是否为空
        if real_sms_code is None:
            return HttpResponse(request, 'register.html', {'error_message': '验证码已经过期'})
        # 判断用户输入的验证码是否正确
        if sms_code !=real_sms_code.decode():
            return HttpResponse(request, 'register.html', {'error_message': '短信验证码错误'})

        # 讲获取的数据保存到数据库中
        # 状态保持
        user=User.objects.create_user(username=username,mobile=mobile,password=pwd1)
        # 状态保持
        # 注册成功后返回首页
        login(request,user)
        return redirect('/')


class UserLoginView(View):
    def get(self,request):
        # 返回登路界面
        return render(request,'login.html',{'loginerror':'密码错误'})

    def post(self,request):

        # 获取`数据
        data=request.POST
        username=data.get('username')
        password=data.get('pwd')
        remembered=data.get('remembered')
        next=request.GET.get('next')
        if next is None:
            next = '/'

        # 数据验证
        # if username is None or password is None or username=='':
        #     return render(request,'login.html',{'loginerror':'数据不能为空'})
        # try:
        #     user=User.objects.get(username=username)
        #
        # except:
        #     return render(request,'login.html',{'loginerror':'用户名错误'})
        #
        # # 校验密码
        # if not user.check_password(password):
        #     return render(request,'login.html',{'loginerror':'密码错误'})
        #
        # if user is None:
        #     return render(request,'login.html',{'loginerror':'用户明活密码错误'})
        # 使用自定义的用户方法 authenticate
        user=authenticate(request,username=username,password=password)

        if user is None:
            return render(request,'login.html',{'loginerror':'用户明活密码错误'})

        login(request,user)
        # 判断用户是否选择记住登陆
        if remembered=='on':
            request.session.set_expiry(60*60*7)
            response=redirect(next)
            response.set_cookie('username',username,60*60*24*7)
        else:

            request.session.set_expiry(60 * 60 * 2)
            response = redirect(next)
            response.set_cookie('username', username, 60 * 60 * 2)
        return  response

class UserLogoutView(View):
    # 退出登陆
    def get(self,request):
        # 使用django认证的系统方法完成退出登陆 删除session数据
        logout(request)

        response=redirect('/login/')
        if request.COOKIES.get('username'):
            # 删除cookie中的username
            response.delete_cookie('username')

        return  response
# 利用装饰其实现判断用户的登陆
method_decorator(login_required,name='dispatch')
# 判断用户是否已经登陆了
class UserInfoView(View):
    # 用户中心
    def get(self,request):
        return render(request,'user_center_info.html')


# 验证邮箱的有效性
class UserEmailView(View):
    def put(self,request):

        # 获取json书库用户的基本信息
        data=request.body.decode()
        # 讲json数据转化为字典
        data_dict=json.loads(data)
        # 获取邮箱信息数据 标题 邮件信息内容  收件人信息内容 列表【收件人的邮箱】
        to_emali=data_dict['email']
        # 验证邮箱的有效性
        # send_mall
        # 更新邮箱数据
        user=request.user
        tjs=TJS(settings.SECRET_KEY,300)
        token = tjs.dumps({'username': user.username, 'email':to_emali}).decode()
        verify_url=settings.EMAIL_VERIFY_URL+'?token=%s'%token
        subject='梅朵邮箱'
        html_message='<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用美多商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (to_emali, verify_url, verify_url)
        # 判断用户是否使用正茬方式登陆
        send_mail(subject, '', settings.EMAIL_FROM, ['18536109028@163.com'], html_message=html_message)
        if not user.is_authenticated:
            return JsonResponse({'code':'4101'})
        user.email=to_emali

        # 保存
        user.save()
        # 正确登陆状态的
        return JsonResponse({'code':'0'})