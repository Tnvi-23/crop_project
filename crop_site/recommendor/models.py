from django.db import models
from django.contrib.auth.models import User
class UserProfile(models.Model):
    user = models.OneToOneField(User, verbose_name=(""), on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return User.username

class prediction(models.Model):
    user = models.ForeignKey(User, verbose_name=(""), on_delete=models.CASCADE)
    n = models.FloatField()
    p = models.FloatField()
    k = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    ph = models.FloatField()
    rainfall = models.FloatField()
    predicted_label = models.CharField(max_length= 1000)
    created_at = models.DateTimeField( auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} --> {self.predicted_label}"

class meta:
    ordering = ['-created_at']