from django.db import models


# Create your models here.
class Category(models.Model):
    # Overwrite the default django pluralisation \
    #  which adds an 's' to the model name
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    category = models.ForeignKey('Category',
                                 null=True,
                                 blank=True,
                                 on_delete=models.SET_NULL)
    name = models.CharField(max_length=254)
    description = models.TextField(null=True,
                                   blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image_url = models.URLField(max_length=1024,
                                null=True,
                                blank=True)
    image = models.ImageField(null=True, blank=True)
    sku = models.CharField(max_length=254,
                           null=True,
                           blank=True)
    size_s = models.BooleanField(default=False,
                                 null=True,
                                 blank=True)
    size_m = models.BooleanField(default=False,
                                 null=True,
                                 blank=True)
    size_lg = models.BooleanField(default=False,
                                  null=True,
                                  blank=True)
    size_xl = models.BooleanField(default=False,
                                  null=True,
                                  blank=True)
    number_of_reviews = models.IntegerField(blank=True,
                                            null=True)

    def __str__(self):
        return self.name
