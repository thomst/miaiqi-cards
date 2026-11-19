from decimal import Decimal
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from simple_page.models import Section
from miaiqi_cards.postcards.models import Postcard, PostcardSet


class ShopSection(Section):
    title = models.CharField(max_length=100)
    order_text = models.TextField(blank=True)
    checkout_text = models.TextField(blank=True)
    confirmation_text = models.TextField(blank=True)

    def __str__(self):
        return self.title


class ProductManager(models.Manager):
    def get_from_content(self, content):
        """Return the product of a postcard or postcard set."""
        return self.get(
            content_type=ContentType.objects.get_for_model(content),
            object_id=content.pk,
        )


class Product(models.Model):
    POSTCARD_PRICE = Decimal("2.20")
    SET_DISCOUNT = POSTCARD_PRICE / 6

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=models.Q(
            app_label=Postcard._meta.app_label,
            model__in=(Postcard._meta.model_name, PostcardSet._meta.model_name),
        ),
    )
    object_id = models.PositiveBigIntegerField()
    content = GenericForeignKey('content_type', 'object_id')

    objects = ProductManager()

    @property
    def price(self):
        if self.content_type.model == Postcard._meta.model_name:
            return self.POSTCARD_PRICE
        else:
            discount = self.SET_DISCOUNT * self.content.postcards.count()
            price = self.POSTCARD_PRICE * self.content.postcards.count()
            return round(price - discount, 2)

    def __str__(self):
        if self.content_type.model == Postcard._meta.model_name:
            return f'{self.content.title} - {self.price} €'
        else:
            return f'{self.content.title} - {self.content.postcards.count()} cards - {self.price} €'

    class Meta:
        unique_together = (('content_type', 'object_id'),)
