import re
from django.db import models
from django.utils.text import slugify
from reorder_items_widget import ReorderItemsField
from simple_page.models import Section, Page


class MiaiqiCardsPage(Page):
    REGIONS = [
        ('main', 'Main Region'),
        ('footer', 'Footer'),
    ]

    class Meta:
        proxy = True


class CSSMixin:
    def css_class(self):
        return re.sub(r'(?<!^)(?=[A-Z])', '-', type(self).__name__).lower()

    def css_id(self):
        return f"{slugify(self.title)}-section"


class WelcomeSection(CSSMixin, Section):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    postcards = models.ManyToManyField('postcards.Postcard')
    title_ref = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='welcome_title')
    subtitle_ref = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='welcome_subtitle')
    postcard_ref = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='welcome_postcard')


class TextSection(CSSMixin, Section):
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)

    def __str__(self):
        return self.title


class FooterSection(Section):
    body = models.TextField(blank=True)


class GalleryPostcard(models.Model):
    gallery = models.ForeignKey('Gallery', on_delete=models.CASCADE)
    postcard = models.ForeignKey('postcards.Postcard', on_delete=models.CASCADE)
    index = ReorderItemsField()

    class Meta:
        unique_together = ('gallery', 'postcard')


class Gallery(CSSMixin, Section):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    postcards = models.ManyToManyField(
        'postcards.Postcard',
        through=GalleryPostcard,
        related_name='galleries',
    )

    def __str__(self):
        return self.title
