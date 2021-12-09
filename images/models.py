from django.db import models
from django.contrib.auth.models import User

class Image(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    image = models.CharField(max_length=200)