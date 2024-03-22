from django.db import models
from usershome.models import CustomUser

# Create your models here.


class Category(models.Model):
    name = models.CharField(unique=True)
    image = models.ImageField(upload_to="category_image/")
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-id"]


class CategoryOffer(models.Model):
    discount_percentage = models.IntegerField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="category_offers"
    )
    valid_from = models.DateField(auto_now_add=True)
    valid_to = models.DateField()
    status = models.CharField(max_length=10, default="Active")

    class Meta:
        ordering = ["-id"]


class Brand(models.Model):
    name = models.CharField(unique=True)
    image = models.ImageField(upload_to="brand_image/")
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-id"]


class Product(models.Model):
    name = models.CharField(unique=True)
    description = models.TextField()
    type = models.CharField()
    price = models.IntegerField()
    offer_price = models.IntegerField(null=True)
    thumbnail = models.ImageField(upload_to="product_thumbnail/")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-id"]

    def thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return None


class ProductOffer(models.Model):
    discount_percentage = models.IntegerField()
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_offers"
    )
    valid_from = models.DateField(auto_now_add=True)
    valid_to = models.DateField()
    status = models.CharField(max_length=10, default="Active")

    class Meta:
        ordering = ["-id"]


class ProductVariant(models.Model):
    color = models.CharField(max_length=100)
    quantity = models.IntegerField()
    thumbnail = models.ImageField(upload_to="product_variant_thumbnail/")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.color

    class Meta:
        ordering = ["-id"]


class Image(models.Model):
    image = models.ImageField(upload_to="product_variant_image/")
    productvariant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)


class Coupons(models.Model):
    code = models.CharField(max_length=15, unique=True)
    description = models.TextField()
    minimum_amount = models.IntegerField()
    discount_percentage = models.IntegerField()
    valid_from = models.DateField(auto_now_add=True)
    valid_to = models.DateField()
    status = models.CharField(max_length=10, default="Active")

    class Meta:
        ordering = ["-id"]


class UsedCoupons(models.Model):
    code = models.ForeignKey(Coupons, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-id"]
