from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from miaiqi_cards.postcards.models import Postcard, PostcardSet
from .models import Product


@receiver(post_save, sender=Postcard, dispatch_uid='shop.create_product_for_postcard')
@receiver(post_save, sender=PostcardSet, dispatch_uid='shop.create_product_for_postcard_set')
def create_product_for_content(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(sender)
    Product.objects.get_or_create(
        content_type=content_type,
        object_id=instance.pk,
    )


@receiver(post_delete, sender=Postcard, dispatch_uid='shop.delete_product_for_postcard')
@receiver(post_delete, sender=PostcardSet, dispatch_uid='shop.delete_product_for_postcard_set')
def delete_product_for_content(sender, instance, **kwargs):
    content_type = ContentType.objects.get_for_model(sender)
    Product.objects.filter(
        content_type=content_type,
        object_id=instance.pk,
    ).delete()
