from django.db import models
from simple_page.models import Section
from ..postcards.models import GallerySection


class ShopSection(Section):
    title = models.CharField(max_length=100)
    order_text = models.TextField(blank=True)
    checkout_text = models.TextField(blank=True)
    confirmation_text = models.TextField(blank=True)
    gallery = models.OneToOneField(GallerySection, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Price(models.Model):
    size = models.DecimalField(max_digits=3, decimal_places=1)
    price = models.DecimalField(max_digits=3, decimal_places=2)
    shop = models.ForeignKey(ShopSection, related_name='prices', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.size} / {self.price}'
