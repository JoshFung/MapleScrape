from django.db import models


class Product(models.Model):
    store = models.CharField(max_length=25)
    name = models.CharField(max_length=350)
    brand = models.CharField(max_length=50)
    normal_price = models.DecimalField(max_digits=7, decimal_places=2)
    sale_price = models.DecimalField(max_digits=7, decimal_places=2)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    num_of_ratings = models.IntegerField()
    shipping = models.CharField(max_length=25)
    promotion = models.CharField(max_length=150)
    out_of_stock = models.BooleanField()
