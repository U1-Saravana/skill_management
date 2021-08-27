from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_manager = models.BooleanField(default=False)


class Skills(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    skill_name = models.CharField(max_length=100)
    score = models.PositiveIntegerField()