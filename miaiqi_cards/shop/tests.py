from django.test import TestCase
from django.db import IntegrityError, transaction
from django.contrib.contenttypes.models import ContentType
from miaiqi_cards.postcards.models import Postcard, PostcardSet
from .models import Product


class ProductTest(TestCase):
    def product_for(self, instance):
        return Product.objects.get(
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.pk,
        )

    def test_saving_postcard_and_set_creates_products(self):
        postcard = Postcard.objects.create(title='Test Postcard')
        postcard_set = PostcardSet.objects.create(
            title='Test Set',
            slug='test-set',
        )

        postcard_product = self.product_for(postcard)
        postcard_set_product = self.product_for(postcard_set)

        self.assertEqual(postcard_product.content, postcard)
        self.assertEqual(postcard_set_product.content, postcard_set)

        postcard.save()
        postcard_set.save()

        self.assertEqual(Product.objects.count(), 2)

    def test_only_one_product_can_point_to_each_object(self):
        postcard = Postcard.objects.create(title='Test Postcard')
        product = self.product_for(postcard)

        with self.assertRaises(IntegrityError), transaction.atomic():
            Product.objects.create(
                content_type=product.content_type,
                object_id=product.object_id,
            )

    def test_deleting_postcard_or_set_deletes_its_product(self):
        postcard = Postcard.objects.create(title='Test Postcard')
        postcard_set = PostcardSet.objects.create(title='Test Set', slug='test-set')

        postcard.delete()
        postcard_set.delete()

        self.assertFalse(Product.objects.exists())
