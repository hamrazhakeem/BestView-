# Generated by Django 5.0.1 on 2024-03-06 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0014_alter_wallettransactions_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallettransactions',
            name='type',
            field=models.CharField(),
        ),
    ]
