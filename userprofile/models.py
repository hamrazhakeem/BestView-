from django.db import models
from usershome.models import CustomUser
from django.core.validators import RegexValidator
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone

# Create your models here.


class Address(models.Model):
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
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-id"]


class Wallet(models.Model):
    balance = models.IntegerField(default=20)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


@receiver(post_save, sender=CustomUser)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        wallet = Wallet.objects.create(user=instance)
        WalletTransactions.objects.create(
            type="Credit", amount=20, date=timezone.now(), wallet=wallet, user=instance
        )


post_save.connect(create_user_wallet, sender=CustomUser)


class WalletTransactions(models.Model):
    amount = models.IntegerField()
    type = models.CharField()
    date = models.DateField(auto_now_add=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-id"]

    @staticmethod
    def save_transaction(type, amount, wallet, user):
        WalletTransactions.objects.create(
            type=type, amount=amount, wallet=wallet, user=user
        )
