from django.db import models


class Order(models.Model):
    cart_id = models.PositiveBigIntegerField(unique=True)
    cart_data = models.JSONField()
    first_name = models.TextField()
    last_name = models.TextField()
    street = models.TextField()
    city = models.TextField()
    postal_code = models.TextField()
    email_address = models.EmailField(max_length=320)
