import re
from django.db import models
from django.utils.text import slugify
from simple_page.models import Section, Page
from ..postcards.models import Gallery
from ..shop.models import Shop


class MiaiqiCardsPage(Page):
    REGIONS = [
        ('main', 'Main Region'),
        ('footer', 'Footer'),
    ]

    class Meta:
        proxy = True


class SectionMixin:
    def css_class(self):
        return re.sub(r'(?<!^)(?=[A-Z])', '-', type(self).__name__).lower()

    def css_id(self):
        return f"{slugify(self.title)}-section"

    def __str__(self):
        return self.title


class WelcomeSection(SectionMixin, Section):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    postcards = models.ManyToManyField('postcards.Postcard')
    title_ref = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='welcome_title')
    subtitle_ref = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='welcome_subtitle')
    postcard_ref = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='welcome_postcard')


class TextSection(SectionMixin, Section):
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)


class GallerySection(SectionMixin, Section):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    gallery = models.OneToOneField(Gallery, null=True, on_delete=models.SET_NULL)


class ShopSection(SectionMixin, Section):
    title = models.CharField(max_length=100)
    body = models.TextField(blank=True)
    shop = models.OneToOneField(Shop, null=True, on_delete=models.SET_NULL)


class FooterSection(Section):
    name = models.CharField(max_length=100, blank=True)
    body = models.TextField(blank=True)

    def __str__(self):
        return self.name
