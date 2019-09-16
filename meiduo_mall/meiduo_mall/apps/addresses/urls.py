from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
   url(r'^addresses',views.AddressView.as_view()),
   # 获取省信息
   url(r'^areas/$', views.AreasView.as_view()),
#    保存收貨地址
   url(r'addresses/create/$',views.AddressCreateView.as_view()),
#    修改收貨地址
#    url(r'addresses//(?P<pk>\d+)/$',views.AddressDefaultView.as_view()),
#    url(r'^addresses/(?P<pk>\d+)/default/$', views.AddressDefaultView.as_view()),
#    # 设置地址标题
#    url(r'^addresses/(?P<pk>\d+)/title/$', views.AddressTitleView.as_view()),

]
