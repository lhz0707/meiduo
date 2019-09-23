from django.conf.urls import url
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token
from .views import statistical
urlpatterns=[
    url(r'^authorizations/$', obtain_jwt_token),
    # 用户总数统计
    url(r'^statistical/total_count/$', statistical.UserTotalCount.as_view()),
    # 日增用户统计
    url(r'^statistical/day_increment/$', statistical.UserDayCount.as_view()),
# 日活用户统计
    url(r'^statistical/day_active/$', statistical.UserDayActiveCount.as_view()),
    # 下单用户用户统计
    url(r'^statistical/day_orders/$', statistical.UserDayOrdersCount.as_view()),
# 月增用户用户统计
    url(r'^statistical/month_increment/$', statistical.UserMonthCount.as_view()),
    # 商品分类访问量统计
    url(r'^statistical/goods_day_views/$', statistical.GoodsTypeCount.as_view()),



]