# 自定义判断用户登陆的方式
from django.contrib.auth.backends import ModelBackend
import re
from users.models import User

class UserUtils(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断用户登陆的方式
        if request is None:
            try:
                user=User.objects.get(username=username,is_staff=True)
            except:
                user=None
            if user is not None and user.check_password(password):
                return user
        else:
            try:
                if re.match(r'1[3-9]\d{9}',username):
                    user=User.objects.get(mobile=username)

                else:
                    user=User.objects.get(username=username)
            except:

                user=None

            # 判断获取的用户对象密码是否正确
            if user is not None and user.check_password(password):
                return user