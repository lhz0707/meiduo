from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns=[

    # 保存購物車數據
    url(r'^carts/$',views.CartView.as_view()),
    # 全選
    url(r'^carts/selection/$', views.CartSelectionView.as_view()),
    # 获取简单购物车数据
    url(r'^carts/simple/$', views.CartSimpleView.as_view()),
]
