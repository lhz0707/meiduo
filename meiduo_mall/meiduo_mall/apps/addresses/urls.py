from django.conf.urls import url
from django.contrib import admin
from . import views
urlpatterns = [
   url(r'^addresses',views.AddressView.as_view())

]
