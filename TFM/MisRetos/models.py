from django.db import models


class Usuario(models.Model):
    email = models.EmailField()
    nombre = models.CharField(max_length=100)
