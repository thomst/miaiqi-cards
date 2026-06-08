import re
from django.db import models
from markdownx.models import MarkdownxField
from reorder_items_widget import ReorderItemsField
from simple_page.models import Section, Page


class MiaiqiCardsPage(Page):
    REGIONS = [
        ('main', 'Main Region'),
        ('footer', 'Footer'),
    ]

    subtitle = models.CharField(max_length=255)
    background_image = models.ImageField(upload_to='backgrounds/')


class CSSMixin:
    def css_class(self):
        return re.sub(r'(?<!^)(?=[A-Z])', '-', type(self).__name__).lower()


class TextSection(CSSMixin, Section):
    title = models.CharField(max_length=255)
    body = MarkdownxField(blank=True)

    def __str__(self):
        return self.title


class FooterSection(Section):
    body = MarkdownxField(blank=True)


class GalleryPostcard(models.Model):
    gallery = models.ForeignKey('Gallery', on_delete=models.CASCADE)
    postcard = models.ForeignKey('Postcard', on_delete=models.CASCADE)
    index = ReorderItemsField()

    class Meta:
        unique_together = ('gallery', 'postcard')


class Postcard(models.Model):
    title = models.CharField(max_length=200)
    description = MarkdownxField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='postcards/')
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Gallery(CSSMixin, Section):
    title = models.CharField(max_length=100)
    description = MarkdownxField(blank=True)
    postcards = models.ManyToManyField(
        Postcard,
        through=GalleryPostcard,
        related_name='galleries',
        )

    def __str__(self):
        return self.title
