# Generated by Django 5.0.1 on 2024-02-24 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_order_and_payment', '0008_alter_orderitems_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitems',
            name='payment_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid')]),
        ),
    ]
