from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
    # 构建支付连接
    url(r'^payment/(?P<order_id>\d+)/$', views.PayMentView.as_view()),
    # 保存支付结果
    url(r'^payment/status/$', views.PayMentStatusView.as_view()),


]
