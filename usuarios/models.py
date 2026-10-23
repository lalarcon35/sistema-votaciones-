from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    documento = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Numero de Documento"
    )
    
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="Telefono"
    )
    

# Create your models here.

def __str__(self):
    return f"{self.first_name}{self.last_name}({self.documento})"
    