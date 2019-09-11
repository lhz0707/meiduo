# 使用中间件判断用户登陆
from django.shortcuts import render,redirect
def myview(get_response):
    def middle(request,*args,**kwargs):
        if request.path in ['/info/','/address/']:
            if not request.user.is_authenticated:
                # 没有获取用登陆失败的跳转链接
                return redirect('/login/?next=%s'%request.path)

        response=get_response(request,*args,**kwargs)

        return response
    return  middle
