from django.db import models
from django.urls import reverse
from reorder_items_widget import ReorderItemsField
from simple_page.models import Section
from ..website.models import SectionMixin


class Postcard(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='postcards/')
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('postcard', kwargs=dict(postcard_id=self.pk))

    class Meta:
        db_table = 'website_postcard'


class GallerySection(SectionMixin, Section):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    postcards = models.ManyToManyField(
        'postcards.Postcard',
        through='GalleryPostcard',
        related_name='galleries',
    )


class GalleryPostcard(models.Model):
    gallery = models.ForeignKey(GallerySection, on_delete=models.CASCADE)
    postcard = models.ForeignKey(Postcard, on_delete=models.CASCADE)
    index = ReorderItemsField()

    class Meta:
        unique_together = ('gallery', 'postcard')
