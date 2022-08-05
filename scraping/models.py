from django.db import models


class Product(models.Model):
    store = models.CharField(max_length=25, null=True)
    name = models.CharField(max_length=350, null=True)
    brand = models.CharField(max_length=50, null=True)
    normal_price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    sale_price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    num_of_ratings = models.IntegerField(null=True)
    shipping = models.CharField(max_length=25, null=True)
    promotion = models.CharField(max_length=150, null=True)
    out_of_stock = models.BooleanField()
    # item_id = models.CharField(max_length=25, null=True)
