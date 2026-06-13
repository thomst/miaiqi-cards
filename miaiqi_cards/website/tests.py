from django.test import TestCase
from django.urls import reverse
from django.core.files.base import ContentFile
from miaiqi_cards.postcards.models import Postcard
from .models import Gallery, GalleryPostcard


class PostcardModelTest(TestCase):
    def test_postcard_creation(self):
        image_content = b'dummy image content'
        postcard = Postcard.objects.create(
            title="Test Postcard",
            description="A test description",
            image=ContentFile(image_content, name='test.jpg')
        )
        self.assertEqual(postcard.title, "Test Postcard")
        self.assertEqual(str(postcard), "Test Postcard")
        self.assertTrue(postcard.is_public)


class PostcardViewTest(TestCase):
    def setUp(self):
        self.postcard = Postcard.objects.create(
            title="View Test",
            image=ContentFile(b'dummy', name='test.jpg')
        )
        self.gallery = Gallery.objects.create(title="Test Gallery")
        GalleryPostcard.objects.create(gallery=self.gallery, postcard=self.postcard, index=0)

    def test_postcard_view(self):
        response = self.client.get(reverse('postcards:postcard', args=[self.gallery.pk, self.postcard.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View Test")
