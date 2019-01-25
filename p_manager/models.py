from django.db import models
from django.contrib.auth.models import User


class Password(models.Model):
    pw_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    pass_id = models.CharField('ID', max_length=26, primary_key=True)
    pw = models.CharField('パスワード', max_length=300)
    purpose = models.TextField('使用場所')
    description = models.TextField('補足')

    def __str__(self):
        return self.pass_id






