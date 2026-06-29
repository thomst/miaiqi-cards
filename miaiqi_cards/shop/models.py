from django.db import models
from simple_page.models import Section
from cart.models import Discount, DiscountType
from ..website.models import SectionMixin
from ..postcards.models import GallerySection


class QuantityDiscountManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(code__startswith=QuantityDiscount.CODE_PREFIX)


class QuantityDiscount(Discount):
    CODE_PREFIX = "QD"

    def save(self, *args, **kwargs):
        self.discount_type = DiscountType.PERCENT
        self.code = f'{self.CODE_PREFIX}-{self.value}-{self.min_cart_value}'
        return super().save(*args, **kwargs)

    class Meta:
        proxy = True
        ordering = ['-min_cart_value']


class ShopSection(SectionMixin, Section):
    title = models.CharField(max_length=100)
    order_text = models.TextField(blank=True)
    checkout_text = models.TextField(blank=True)
    confirmation_text = models.TextField(blank=True)
    gallery = models.OneToOneField(GallerySection, on_delete=models.CASCADE)


class Price(models.Model):
    size = models.DecimalField(max_digits=3, decimal_places=1)
    price = models.DecimalField(max_digits=3, decimal_places=2)
    shop = models.ForeignKey(ShopSection, related_name='prices', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.size} / {self.price}'
