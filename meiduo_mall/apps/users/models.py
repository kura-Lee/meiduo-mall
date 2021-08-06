from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=128)
    mobile = models.CharField(max_length=11, unique=True)

    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name
