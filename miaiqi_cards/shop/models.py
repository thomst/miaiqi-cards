from decimal import Decimal
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from simple_page.models import Section
from miaiqi_cards.postcards.models import Postcard, PostcardSet


class ShopSection(Section):
    title = models.CharField(max_length=100)
    description_text = models.TextField()
    order_text = models.TextField(blank=True)
    checkout_text = models.TextField(blank=True)
    confirmation_text = models.TextField(blank=True)

    privacy_policy = models.FileField(upload_to='legal_documents')
    terms_and_conditions = models.FileField(upload_to='legal_documents')
    cancellation_policy = models.FileField(upload_to='legal_documents')
    model_withdrawal_form = models.FileField(upload_to='legal_documents')

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
    POSTCARD_PRICE = Decimal("2.50")
    SET_DISCOUNT = POSTCARD_PRICE / 5

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
            count = self.content.postcards.count()
            price = self.POSTCARD_PRICE * count - self.SET_DISCOUNT * count
            return round(price, 2)

    def __str__(self):
        if isinstance(self.content, Postcard):
            return self.content.title
        else:
            return f'{self.content.title} ({self.content.postcards.count()} cards)'

    class Meta:
        unique_together = (('content_type', 'object_id'),)


class InvoiceNumber(models.Model):
    """
    The invoice number of a cart is the id of its row. The id is
    auto-incremented by the database, so numbers are consecutive and never
    reused, and the unique cart_id keeps the number stable per cart.
    """
    cart_id = models.PositiveIntegerField(unique=True)

    @classmethod
    def get_invoice_number(cls, cart):
        invoice_number, _ = cls.objects.get_or_create(cart_id=cart.cart.pk)
        return invoice_number.pk
