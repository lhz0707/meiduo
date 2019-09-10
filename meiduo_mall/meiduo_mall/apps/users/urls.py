from django.conf.urls import url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view()),
    # 注册
    url(r'^register/$', views.UserRegisterView.as_view()),
    url(r'^login/$', views.UserLoginView.as_view()),
    # 退出登录
    url(r'^logout/$', views.UserLogoutView.as_view()),
]