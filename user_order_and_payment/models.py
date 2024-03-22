from django.db import models
from usershome.models import CustomUser
from adminproductmanagement.models import Product, ProductVariant
from django.core.validators import RegexValidator
import random
from datetime import datetime, time

# Create your models here.


class OrderAddress(models.Model):
    house_or_building_name = models.CharField()
    street_address = models.CharField()
    city = models.CharField()
    district = models.CharField()
    pincode_regex = RegexValidator(
        regex=r"^\d{6}$", message="Pincode must be 6 'digits'"
    )
    pincode = models.CharField(max_length=6, validators=[pincode_regex])
    state = models.CharField()
    phone_regex = RegexValidator(
        regex=r"^\d{10}$", message="Phone number must be 10 'digits'"
    )
    phone_no = models.CharField(max_length=10, validators=[phone_regex])

    def __str__(self) -> str:
        return super().__str__()


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("Cash On Delivery", "Cash On Delivery"),
        ("PayPal", "PayPal"),
        ("Wallet", "Wallet"),
    ]
    order_id = models.IntegerField(unique=True)
    orderdate = models.DateField(auto_now_add=True)
    total = models.IntegerField()
    paymentmethod = models.CharField(choices=PAYMENT_METHOD_CHOICES)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    orderaddress = models.ForeignKey(OrderAddress, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-id"]

    def _str_(self) -> str:
        return f"{self.user.first_name}-{self.id}"

    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate a random order ID
            self.order_id = random.randint(
                100000, 999999
            )  # You can adjust the range as needed
        super().save(*args, **kwargs)


class OrderItems(models.Model):
    ORDER_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Dispatched", "Dispatched"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
        ("Returned", "Returned"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Refunded", "Refunded"),
        ("Paid", "Paid"),
    ]
    quantity = models.IntegerField()
    subtotal = models.IntegerField()
    deliverydate = models.DateField(null=True, blank=True)
    order_status = models.CharField(choices=ORDER_STATUS_CHOICES, default="Pending")
    payment_status = models.CharField(choices=PAYMENT_STATUS_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-id"]

    def save(self, *args, **kwargs):
        if self.order_status == "Delivered" and self.deliverydate is None:
            delivery_datetime = datetime.combine(self.order.orderdate, time.min)
            self.deliverydate = delivery_datetime.date()
        if self.order_status == "Cancelled" and (
            self.order.paymentmethod == "PayPal" or self.order.paymentmethod == "Wallet"
        ):
            self.payment_status = "Refunded"
        elif (
            self.order_status == "Cancelled"
            and self.order.paymentmethod == "Cash On Delivery"
        ):
            self.payment_status = "Abandoned"
        if self.order_status == "Delivered":
            self.payment_status = "Paid"
        if self.order_status == "Returned":
            self.payment_status = "Refunded"

        super().save(*args, **kwargs)
