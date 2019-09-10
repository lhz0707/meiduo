# 自定义验证模型
from django.contrib.auth.backends import ModelBackend
import re
from users.models import User

class UserUtils(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 判断用户登陆的方式
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