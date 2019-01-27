from django.db import models
from django.contrib.auth.models import User


class Password(models.Model):
    pw_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    pass_id = models.CharField('ID', max_length=26, primary_key=True)
    pw = models.CharField('パスワード', max_length=300)
    purpose = models.TextField('使用場所', max_length=100, blank=True)
    description = models.TextField('補足', max_length=500, blank=True)

    def __str__(self):
        return self.pass_id






