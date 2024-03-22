# Generated by Django 5.0.1 on 2024-03-12 15:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminproductmanagement', '0021_alter_productoffer_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoryoffer',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_offers', to='adminproductmanagement.category'),
        ),
        migrations.AlterField(
            model_name='productoffer',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_offers', to='adminproductmanagement.product'),
        ),
    ]
