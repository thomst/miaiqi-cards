from django.db import models
from cart.models import Discount, DiscountType
from ..postcards.models import Gallery


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


class Shop(models.Model):
    name = models.CharField(max_length=100, blank=True)
    gallery = models.OneToOneField(Gallery, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Price(models.Model):
    size = models.DecimalField(max_digits=3, decimal_places=1)
    price = models.DecimalField(max_digits=3, decimal_places=2)
    shop = models.ForeignKey(Shop, related_name='prices', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.size} / {self.price}'
