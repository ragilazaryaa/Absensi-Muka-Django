from django.db import models

# Create your models here.
class Karyawan(models.Model):
    nik = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    divisi = models.CharField(max_length=50,null=True)
    photo = models.ImageField(upload_to='static/img')

class Absen(models.Model):
    userid = models.AutoField(primary_key=True)
    nik = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

