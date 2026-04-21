from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=80)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    codigo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=120)
    descripcion = models.TextField(default="Sin descripción")
    precio = models.PositiveIntegerField()
    stock = models.PositiveIntegerField()
    imagen = models.CharField(max_length=255)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(default=timezone.now)
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.PositiveIntegerField()

    def __str__(self):
        return f"Venta #{self.id}"


class Detalle(models.Model):
    id = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.PositiveIntegerField()

    def __str__(self):
        return f"Detalle #{self.id} - {self.producto.nombre}"