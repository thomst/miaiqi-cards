from django.test import TestCase
from django.urls import reverse
from django.core.files.base import ContentFile
from .models import Postcard

# Create your tests here.

class PostcardModelTest(TestCase):
    def test_postcard_creation(self):
        # Create a dummy image
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

    def test_postcard_list_view(self):
        response = self.client.get(reverse('postcard_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View Test")

    def test_postcard_view(self):
        response = self.client.get(reverse('postcard', args=[self.postcard.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "View Test")
        self.assertContains(response, "View Test")
