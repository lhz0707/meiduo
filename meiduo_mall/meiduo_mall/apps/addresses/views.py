from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from django.http import JsonResponse
from django.core.cache import cache
import json
import re

class AddressView(View):
    def get(self,request):
        return render(request, 'user_center_site.html')
