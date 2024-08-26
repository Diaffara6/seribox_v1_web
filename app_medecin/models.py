from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Prescription(models.Model):
    med1 = models.CharField(max_length=50, blank=True)
    quant1 = models.IntegerField(default=1)
    med2 = models.CharField(max_length=50, blank=True)
    quant2 = models.IntegerField(default=1)
    med3 = models.CharField(max_length=50, blank=True)
    quant3 = models.IntegerField(default=1)
    med4 = models.CharField(max_length=50, blank=True)
    quant4 = models.IntegerField(default=1)
    cmd = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to="media/")
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


class Medecin(models.Model):
    medecin = models.ForeignKey(User, on_delete=models.CASCADE)
