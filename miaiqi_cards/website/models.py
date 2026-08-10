from django.db import models
from simple_page.models import Section, Page


class MiaiqiCardsPage(Page):
    REGIONS = [
        ('head', 'Document Head'),
        ('main', 'Main Region'),
        ('footer', 'Footer'),
    ]
    description = models.TextField(blank=True)


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
