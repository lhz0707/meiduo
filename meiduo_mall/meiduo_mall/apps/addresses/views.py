from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from addresses.models import Area, Address
from django.http import JsonResponse
from django.core.cache import cache
import json
import re

class AddressView():
    def get(self,request):
        return render(request, 'user_center_site.html')
