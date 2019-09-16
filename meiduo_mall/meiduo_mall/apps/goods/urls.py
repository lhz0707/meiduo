from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns=[
#     列表也頁面渲染
    url(r'^list/(?P<categorie_id>\d+)/(?P<page_num>\d+)/', views.GoodsListView.as_view()),
]