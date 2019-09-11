from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    # 构造一个qq登录的跳转路径
    url(r'^qq/login/$', views.QQLoginView.as_view()),
    # qq跳转路由匹配
    url(r'^oauth_callback/$',views.QQCallBackView.as_view())
]
