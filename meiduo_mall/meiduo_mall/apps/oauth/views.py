from django.shortcuts import render,redirect
from django.http import JsonResponse,HttpResponse
from django.contrib.auth import login
from django.conf import settings
from django.views import View
from QQLoginTool.QQtool import OAuthQQ

from oauth.models import OAuthQQUser
from  django_redis import get_redis_connection
from users.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as TJS

class QQLoginView(View):
    def get(self, request):
        # 获取登录成功后的跳转连接
        next = request.GET.get('next')
        if next is None:
            next = '/'
        # 1、初始化创建qq对象
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        # 2、调用方法生成跳转连接
        login_url = qq.get_qq_url()
        # 3、返回跳转连接
        return JsonResponse({'login_url': login_url})

class QQCallBackView(View):
    def get(self,request):
#         获取用户的code值  和状态信息
        code=request.GET.get('code')
        state=request.GET.get('state')
        if code is None or state is None:
            return JsonResponse({'error':'缺少数据'},state=400)

        # 生成qq对象
        qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                     redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        # 获取access_token
        try:
            access_token=qq.get_access_token(code)
            open_id=qq.get_open_id(access_token)

        # 调用方法获取open_id的值
        except:
            return JsonResponse({'error':'网络错误'},state=400)


        # 判断用户是否绑定梅朵用户
        try:
            # 查询mysql数据表中是否有此qq用户
            qq_user=OAuthQQUser.objects.get(openid=open_id)
        except:
            tjs = TJS(settings.SECRET_KEY, 300)
            openid = tjs.dumps({'openid': open_id}).decode()
            return render(request, 'oauth_callback.html', {'token': openid})

        login(request,qq_user.user)

        # 没有异常说明qq查询到绑定的qq用户
        # 将用户名写入cookie中 在页面中显示
        response=redirect(state)
        response.set_cookie('username',qq_user.user.username,60*60*2)


        return  response

    def post(self,request):
        #绑定qq用户
        data=request.POST
        mobile=data.get('mobile')
        password=data.get('pwd')
        sms_code=data.get('sms_code')
        openid=data.get('access_token')

        # 验证数据
        # 短信验证
        client=get_redis_connection('verfycode')
        real_sms_code=client.get('sms_code_%s'%mobile)

        if real_sms_code is None:
            return render(request, 'oauth_callback.html', {'errmsg': '短信验证码已失效'})
        if sms_code != real_sms_code.decode():
            return render(request, 'oauth_callback.html', {'errmsg': '短信验证码错误'})
        # 3、绑定数据

        try:
            user=User.objects.get(mobile=mobile)
            # 验证qq用户的密码是否正确
            if not user.check_password(password):
                return render(request,'oauth_callback.html',{'errmsg': '密码错误'})
        except:
            # 当前用户为注册为梅朵用户 注册新用户
            user=User.objects.create_user(username=mobile,mobile=mobile,password=password)

        tjs = TJS(settings.SECRET_KEY, 300)
        try:
            data = tjs.loads(openid)
        except:
            return render(request, 'oauth_callback.html', {'errmsg': 'openid异常'})
        openid = data.get('openid')
        OAuthQQUser.objects.create(openid=openid, user=user)
        return  redirect('/')