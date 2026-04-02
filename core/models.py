from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=40)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    codigo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=40)
    descripcion = models.CharField(max_length=250, default="Sin Descripción")
    precio = models.IntegerField()
    stock = models.IntegerField()
    imagen = models.CharField(max_length=255)
    Categoria = models.ForeignKey(to=Categoria,on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Venta(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(default=datetime.now)
    cliente = models.ForeignKey(to=User, on_delete=models.CASCADE)
    total = models.IntegerField()

class Detalle(models.Model):
    id = models.AutoField(primary_key=True)
    venta = models.ForeignKey(to=Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(to=Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.IntegerField()


