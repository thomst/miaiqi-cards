from datetime import date

from django.db import IntegrityError, models, transaction
from django.db.models import Max


class InvoiceNumber(models.Model):
    """
    The invoice number of a cart. The numbers start at 1 each year, so only
    the combination of year and number is unique. The unique cart_id keeps
    the number stable per cart.
    """
    cart_id = models.PositiveIntegerField(unique=True)
    year = models.PositiveIntegerField()
    number = models.PositiveIntegerField()

    class Meta:
        unique_together = (('year', 'number'),)

    @classmethod
    def get_invoice_number(cls, cart):
        year = date.today().year
        while True:
            try:
                with transaction.atomic():
                    try:
                        entry = cls.objects.get(cart_id=cart.cart.pk)
                    except cls.DoesNotExist:
                        last = cls.objects.filter(year=year).aggregate(Max('number'))['number__max']
                        entry = cls.objects.create(cart_id=cart.cart.pk, year=year, number=(last or 0) + 1)
                    return entry.number
            except IntegrityError:
                # A concurrent request took the number; try again with the new maximum.
                continue
