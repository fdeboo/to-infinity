from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=75)
    friendly_name = models.CharField(max_length=75, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    category = models.ForeignKey(
        "Category", null=True, blank=True, on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=254)
    product_id = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(null=True, blank=True)
    image_thumb = models.ImageField(null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.name


class AddOn(Product):
    min_medical_threshold = models.IntegerField(
        default=0, null=False, blank=False
    )

    def __str__(self):
        return self.name


class Insurance(Product):
    friendly_name = models.CharField(max_length=75, blank=True)

    def __str__(self):
        return self.name


class Destination(Product):
    max_passengers = models.IntegerField(null=True, blank=True)
    duration = models.CharField(max_length=20, blank=True)
    min_medical_threshold = models.IntegerField(
        default=0, null=False, blank=False
    )

    def __str__(self):
        return self.name
