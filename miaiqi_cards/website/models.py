from django.db import models
from django.urls import reverse
from simple_page.models import Section, Page


class MiaiqiCardsPage(Page):
    REGIONS = [
        ('main', 'Main Region'),
        ('footer', 'Footer'),
    ]
    description = models.TextField(blank=True)

    def get_absolute_url(self):
        return reverse('page')


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
