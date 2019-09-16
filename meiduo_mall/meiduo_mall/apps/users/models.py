from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    """自定义用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    # 增加字段用来验证邮箱的有效性
    email_actice=models.BooleanField(default=False,verbose_name="邮箱的有效性")

    # 添加默認模型累
    default_address = models.ForeignKey('addresses.Address', related_name='users', null=True, blank=True)
    class Meta:
        db_table = 'tb_users'
