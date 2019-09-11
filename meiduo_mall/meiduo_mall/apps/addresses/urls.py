from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
   url(r'^addresses',views.AddressView.as_view()),
   # 获取省信息
   url(r'^areas/$', views.AreasView.as_view()),

]
