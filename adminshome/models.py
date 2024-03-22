from django.db import models

# Create your models here.


class Banner(models.Model):
    name = models.CharField()
    image = models.ImageField(upload_to="banner_image/")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-id"]
