from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns=[
#     列表也頁面渲染
    url(r'^list/(?P<categorie_id>\d+)/(?P<page_num>\d+)/', views.GoodsListView.as_view()),
    # 获取热销商品
    url(r'hot/(?P<categorie_id>\d+)/$', views.GoodsHotView.as_view()),

   # 搜索
    url(r'search/$',views.GoodsSearchView.as_view()),

#     商品详情页渲染
    url(r'detail/(?P<pk>\d+)/$',views.GoodsDetailVIew.as_view())
]