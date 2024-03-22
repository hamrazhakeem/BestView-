from django.db import models
from usershome.models import CustomUser
from adminproductmanagement.models import Product, ProductVariant

# Create your models here.


class Cart(models.Model):
    total = models.IntegerField(default=0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


class CartItem(models.Model):
    quantity = models.IntegerField(default=1)
    subtotal = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-id"]


class Wishlist(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
