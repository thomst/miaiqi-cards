import re
from django.db import models
from django.utils.text import slugify
from simple_page.models import Section, Page


class MiaiqiCardsPage(Page):
    REGIONS = [
        ('head', 'Document Head'),
        ('main', 'Main Region'),
        ('footer', 'Footer'),
    ]
    description = models.TextField(blank=True)


class WelcomeSection(Section):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    postcards = models.ManyToManyField('postcards.Postcard')
    title_ref = models.ForeignKey(Section, null=True, on_delete=models.SET_NULL, related_name='welcome_title')
    subtitle_ref = models.ForeignKey(Section, null=True, on_delete=models.SET_NULL, related_name='welcome_subtitle')
    postcard_ref = models.ForeignKey(Section, null=True, on_delete=models.SET_NULL, related_name='welcome_postcard')

    def __str__(self):
        return self.title


class TextSection(Section):
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)

    def __str__(self):
        return self.title


class FooterSection(Section):
    name = models.CharField(max_length=100, blank=True)
    body = models.TextField(blank=True)

    def __str__(self):
        return self.name
